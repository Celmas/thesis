import requests
import json
import pandas as pd

query = """query { 
  user(login:"real-or-random") { 
    followers {
      totalCount
    }
    bio
    repositories(last:100) {
      nodes {
        name
        repositoryTopics(last:15) {
          totalCount
          nodes {
            topic {
              name
            }
          }
        }
        description
        watchers {
          totalCount
        }
        languages(first:5) {
          nodes {
            name
          }
        }
        issues {
          totalCount
        }
        pullRequests {
          totalCount
        }
        isFork
        forkCount
        url
        primaryLanguage {
          name
        }
         object(expression: "master:README.md") {
    		  ... on Blob {
        		text
     		 }
        }
      }
    }
    contributionsCollection {
      totalRepositoryContributions
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      commitContributionsByRepository {
        contributions(last:50) {
          totalCount
          nodes {
            repository {
              description
              name
            }
          }
        }
      }
    }
  }
}"""

url = 'https://rickandmortyapi.com/graphql/'
r = requests.post(url, json={'query': query})
print(r.status_code)
print(r.text)

json_data = json.loads(r.text)