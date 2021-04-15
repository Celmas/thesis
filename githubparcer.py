import requests
import json
import sqlite3 as lite


def save_user(conn, user_tuple):
    cur = conn.cursor()
    insert_user_query = """INSERT INTO user
                          (name, bio, followers, total_repository_contributions, total_commit_contributions,
                           total_issues_contributions, total_pull_request_contributions, 
                           total_pull_request_review_contributions)
                          VALUES
                          (?, ?, ?, ?, ?, ?, ?, ?);"""
    cur.execute(insert_user_query, user_tuple)
    _user_id = cur.lastrowid
    cur.close()
    return _user_id


def save_repo(conn, repository_tuple):
    cur = conn.cursor()
    insert_repo_query = """INSERT INTO repositories
                          (user_id, name, description, watchers, issues, pull_requests,
                           is_fork, fork_count, url, primary_language,
                           repository_topics_count, readme)
                          VALUES
                          (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
    cur.execute(insert_repo_query, repository_tuple)
    _repo_id = cur.lastrowid
    cur.close()
    return _repo_id


def save_topic(conn, topic_tuple):
    cur = conn.cursor()
    insert_topic_query = """INSERT INTO repository_topics
                          (repository_id, name)
                          VALUES
                          (?, ?);"""
    cur.execute(insert_topic_query, topic_tuple)
    _topic_id = cur.lastrowid
    cur.close()
    return _topic_id


def save_language(conn, language_tuple):
    cur = conn.cursor()
    insert_lang_query = """INSERT INTO languages
                          (repository_id, name)
                          VALUES
                          (?, ?);"""
    cur.execute(insert_lang_query, language_tuple)
    _lang_id = cur.lastrowid
    cur.close()
    return _lang_id


def save_contribution(conn, contribution_tuple):
    cur = conn.cursor()
    insert_contr_query = """INSERT INTO commit_contributions_by_repository
                          (user_id, total_count, repository_name, repository_description)
                          VALUES
                          (?, ?, ?, ?);"""
    cur.execute(insert_contr_query, contribution_tuple)
    _contr_id = cur.lastrowid
    cur.close()
    return _contr_id


def update_processed_flag(conn, user_id, flag=True):
    cur = conn.cursor()
    _tuple = (flag, user_id)
    update_processed_flag_query = """UPDATE user_log SET is_processed = ? WHERE id = ?;"""
    cur.execute(update_processed_flag_query, _tuple)
    conn.commit()
    cur.close()


def get_unprocessed_users(conn):
    cur = conn.cursor()
    select_unprocessed_users_query = """SELECT * FROM user_log WHERE is_processed = 0 LIMIT 2000"""
    cur.execute(select_unprocessed_users_query)
    records = cur.fetchall()
    print("Fetched " + str(len(records)) + " users")
    cur.close()
    return records


query = """query { 
  user(login:"$login") { 
    name
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


def job():
    print("First 2000 users is about to be parsed")
    connection = lite.connect('githubdataset.db')
    connection.isolation_level = None
    url = 'https://api.github.com/graphql'
    headers = {'Authorization': 'bearer '}
    users_to_process = get_unprocessed_users(connection)
    for user_row in users_to_process:
        print("Start processing user: " + user_row[2])
        formatted_query = query.replace("$login", f'{user_row[2]}')

        try:
            r = requests.post(url, json={'query': formatted_query}, headers=headers)

            json_data = json.loads(r.text)
            connection.execute("BEGIN")

            name = json_data['data']['user']['name']
            bio = json_data['data']['user']['bio']
            followers = json_data['data']['user']['followers']['totalCount']
            totalRepositoryContributions = json_data['data']['user']['contributionsCollection'][
                'totalRepositoryContributions']
            totalCommitContributions = json_data['data']['user']['contributionsCollection']['totalCommitContributions']
            totalIssueContributions = json_data['data']['user']['contributionsCollection']['totalIssueContributions']
            totalPullRequestContributions = json_data['data']['user']['contributionsCollection'][
                'totalPullRequestContributions']
            totalPullRequestReviewContributions = json_data['data']['user']['contributionsCollection'][
                'totalPullRequestReviewContributions']
            user = (name, bio, followers, totalRepositoryContributions, totalCommitContributions, totalIssueContributions, totalPullRequestContributions, totalPullRequestReviewContributions)

            user_id = save_user(connection, user)
            repos = json_data['data']['user']['repositories']['nodes']
            for repo in repos:
                repo_name = repo['name']
                repo_description = str(repo['description'] or '')
                repo_watchers = repo['watchers']['totalCount']
                repo_issues = repo['issues']['totalCount']
                repo_pull_requests = repo['pullRequests']['totalCount']
                repo_is_fork = repo['isFork']
                repo_fork_count = repo['forkCount']
                repo_url = repo['url']
                repo_primary_language = ''
                if repo['primaryLanguage'] is not None:
                    repo_primary_language = repo['primaryLanguage']['name']
                repo_topics_count = repo['repositoryTopics']['totalCount']
                repo_readme = ''
                if repo['object'] is not None:
                    repo_readme = str(repo['object']['text'] or '')
                repository = (user_id, repo_name, repo_description, repo_watchers, repo_issues, repo_pull_requests, repo_is_fork, repo_fork_count, repo_url, repo_primary_language, repo_topics_count, repo_readme)
                repo_id = save_repo(connection, repository)

                if repo_topics_count > 0:
                    repo_topics = repo['repositoryTopics']['nodes']
                    for topic in repo_topics:
                        topic_name = topic['topic']['name']
                        _topic = (repo_id, topic_name)
                        save_topic(connection, _topic)

                if len(repo['languages']['nodes']) > 0:
                    repo_languages = repo['languages']['nodes']
                    for lang in repo_languages:
                        lang_name = lang['name']
                        language = (repo_id, lang_name)
                        save_language(connection, language)

            contributions_by_repository = json_data['data']['user']['contributionsCollection'][
                'commitContributionsByRepository']
            for contribution in contributions_by_repository:
                contr_count = contribution['contributions']['totalCount']
                contr_repo_name = contribution['contributions']['nodes'][0]['repository']['name']
                contr_repo_description = str(
                    contribution['contributions']['nodes'][0]['repository']['description'] or '')
                _contribution = (user_id, contr_count, contr_repo_name, contr_repo_description)
                save_contribution(connection, _contribution)
        except requests.exceptions.RequestException:
            print("Caught exception due to request")
            continue
        except TypeError:
            print("Caught exception due to parsing")
            connection.execute("ROLLBACK")
            continue
        except connection.Error:
            print("Caught exception from sql")
            connection.execute("ROLLBACK")
            continue
        connection.execute("COMMIT")

        update_processed_flag(connection, user_row[0])
        print("User: " + str(user_row[2]) + " was processed")

    print("Done")

job()
