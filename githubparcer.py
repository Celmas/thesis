import requests
import json
import pandas as pd

query = """query { 
  user(login:"Dyakonov") { 
    followers {
      totalCount
    }
    following {
      totalCount
    }
    pullRequests(last:100) {
      nodes {
        headRepository {
          watchers {
            totalCount
          }
        	issues {
          	totalCount
        	}
        	pullRequests {
          	totalCount
        	}
        }
        merged
      }
    }
    bio
    repositories(first:50) {
      nodes {
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
        url
        forkCount
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
            
            commitCount
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