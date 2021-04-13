import requests
import json
import sqlite3 as lite

query = """query { 
  user(login:"justmarkham") {
    followers (first: 100, after:"$after") {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      nodes {
        login
        name
        url
      }
    }
  }
}
"""

connection = lite.connect('githubdataset.db')
after = 'Y3Vyc29yOjkwMg=='
for i in range(590):
    formatted_query = query.replace("$after", f'{after}')

    url = 'https://api.github.com/graphql'
    headers = {'Authorization': 'bearer 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'}
    r = requests.post(url, json={'query': formatted_query}, headers=headers)
    print('Iteration: ' + str(i))
    print('After = ' + after)

    json_data = json.loads(r.text)

    after = json_data['data']['user']['followers']['pageInfo']['endCursor']
    nodes = json_data['data']['user']['followers']['nodes']
    cur = connection.cursor()
    for node in nodes:
        user_name = node['name']
        user_login = node['login']
        user_url = node['url']
        user = (user_name, user_login, user_url, False)
        insert_user_query = """INSERT INTO user_log
                              (name, login, url, is_processed)
                              VALUES
                              (?, ?, ?, ?);"""
        cur.execute(insert_user_query, user)
    connection.commit()
    cur.close()
