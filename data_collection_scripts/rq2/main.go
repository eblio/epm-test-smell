package main

import (
	"bytes"
	"encoding/csv"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"os"
	"os/exec"
	"path"
	"strings"
	"sync"
	"time"
)

var threads = 12
var commit_file = "commit_file"
var toolsFolder string
var scriptFile string
var reposFile string

type Repository struct {
	url  string
	name string
}

func readRepositories(data [][]string) []Repository {
	var repositories []Repository
	for i, line := range data {
		if i > 0 { // omit header line
			var r Repository
			for j, field := range line {
				if j == 0 {
					r.url = field
				} else if j == 7 {
					r.name = field
				}
			}
			repositories = append(repositories, r)
		}
	}
	return repositories
}

func main() {

	flag.StringVar(&toolsFolder, "t", "tools", "Specify tools folder. Default is tools")
	flag.StringVar(&reposFile, "l", "repos.csv", "Specify repositories .csv. Default is repos.csv")
	flag.StringVar(&scriptFile, "s", "extract_test_smells", "Specify python script to run")

	flag.Parse() // parse flags

	f, err := os.Open(reposFile)
	if err != nil {
		log.Fatal(err)
	}

	defer f.Close()

	csvReader := csv.NewReader(f)
	data, err := csvReader.ReadAll()
	if err != nil {
		log.Fatal(err)
	}

	repositories := readRepositories(data)
	analyseRepositories(repositories)
}

func analyseRepositories(repositories []Repository) {
	for i := 0; i < len(repositories); i++ {
		log.Print("Creating temp dir for ", repositories[i].name)
		dir, err := ioutil.TempDir(".", repositories[i].name)
		if err != nil {
			log.Fatal(err)
		}
		log.Print("Cloning repository for ", repositories[i].name)
		defer os.RemoveAll(dir)
		cmdClone := exec.Command("git", "clone", repositories[i].url, repositories[i].name)
		cmdClone.Dir = dir
		err = cmdClone.Run()
		if err != nil {
			log.Fatal(err)
		}
		log.Print("Create thread dirs for ", repositories[i].name)
		for j := 0; j < threads; j++ {
			threadDir := fmt.Sprintf("%s%d", repositories[i].name, j)
			threadDirPath := path.Join(dir, threadDir)
			err := os.Mkdir(threadDirPath, 0755)
			if err != nil {
				log.Fatal(err)
			}
			cmdCopyRepo := exec.Command("cp", "-r", repositories[i].name, threadDir)
			cmdCopyRepo.Dir = dir
			err = cmdCopyRepo.Run()
			if err != nil {
				log.Fatal(err)
			}

		}

		var outb bytes.Buffer
		cmdGitLog := exec.Command("git", "log", "--all", "--pretty=%H")
		cmdGitLog.Stdout = &outb
		cmdGitLog.Dir = path.Join(dir, repositories[i].name)
		cmdGitLog.Run()
		commitsSha := strings.Split(outb.String(), "\n")
		//Remove last empty line
		commitsSha = commitsSha[:len(commitsSha)-1]
		log.Print("Detecting  ", len(commitsSha), " commits")

		//Shuffle slice for better distribution between threads
		rand.Seed(time.Now().UnixNano())
		rand.Shuffle(len(commitsSha), func(i, j int) { commitsSha[i], commitsSha[j] = commitsSha[j], commitsSha[i] })
		nCommitsByThread := len(commitsSha) / threads
		log.Print("Generating commits list for ", repositories[i].name)
		for j := 0; j < threads; j++ {
			threadDir := fmt.Sprintf("%s%d", repositories[i].name, j)
			threadDirPath := path.Join(dir, threadDir)
			var commits []string
			if j == threads-1 {
				commits = commitsSha[j*nCommitsByThread : (j*nCommitsByThread)+nCommitsByThread+(len(commitsSha)%threads)]
			} else {
				commits = commitsSha[j*nCommitsByThread : (j*nCommitsByThread)+nCommitsByThread]
			}
			f, err := os.Create(path.Join(threadDirPath, commit_file))
			if err != nil {
				log.Fatal(err)
			}
			defer f.Close()
			f.WriteString(strings.Join(commits[:], "\n"))
		}
		analyseRepository(repositories[i], dir)
	}
}

func analyseRepository(repository Repository, repoDir string) {
	log.Print("Starting process for ", repository.name)
	var wg sync.WaitGroup
	wg.Add(threads)
	fmt.Println("")
	for i := 0; i < threads; i++ {
		go func(i int) {
			defer wg.Done()
			threadDir := fmt.Sprintf("%s%d", repository.name, i)
			threadDirPath := path.Join(repoDir, threadDir)
			scriptPath := path.Join("../../", scriptFile)
			toolPath := path.Join("../../", toolsFolder)
			outfile, err := os.Create(path.Join(threadDirPath, "stdout.log"))
			if err != nil {
				log.Fatal(err)
			}
			errfile, err := os.Create(path.Join(threadDirPath, "stderr.log"))
			if err != nil {
				log.Fatal(err)
			}
			defer outfile.Close()
			cmdRunAnalysis := exec.Command("python3", scriptPath, "-u", repository.url, "-n", repository.name, "-t", toolPath, "-c", commit_file)
			cmdRunAnalysis.Dir = threadDirPath
			cmdRunAnalysis.Stdout = outfile
			cmdRunAnalysis.Stderr = errfile
			err = cmdRunAnalysis.Run()
			if err != nil {
				log.Print("Error during analysis process")
				log.Fatal(err)
			}
			log.Print(fmt.Sprintf("Process #%d complete", i))
		}(i)
	}
	wg.Wait()

}
