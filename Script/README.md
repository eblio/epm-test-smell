# Group 1 - Replication in Java

## List the available repositories

We first tried to fetch a repository list by going through F-Droid
APK names and other data set. This method was inefficient as guessing
the repository URL from the APK name is unreliable. We managed to
get more than 600 hundred of valid repositories.

Then we stumbled upon the [F-Droid API](https://f-droid.org/fr/2021/02/05/apis-for-all-the-things.html)
supplying the [list of all applications](https://f-droid.org/repo/index-v1.jar) 
and their open-source repositories. This allowed us to collect more
than 3000 repositories which will be re-filtered soon on their amount
of stars, tags, etc ... 

## Extract data from repositories

Now that we have our repositories prepared, we can start to extract 
some data from it. 

For instance, we extract the repository commits and their modifications
on this format : 

```json
project: {
    commit_hash: {
        modified_file: [
            [
                line_number, modifications
            ]
        ]
    }
}
```

Also, we have run the provided tools on the repositories, but it will
not be discussed there yet.
