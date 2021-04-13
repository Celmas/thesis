CREATE TABLE IF NOT EXISTS user (
	id integer PRIMARY KEY,
	name text,
	bio text,
	followers integer,
	total_repository_contributions integer,
	total_commit_contributions integer,
	total_issues_contributions integer,
	total_pull_request_contributions integer,
	total_pull_request_review_contributions integer
);

CREATE TABLE IF NOT EXISTS repositories (
	id integer PRIMARY KEY,
	user_id integer,
	name text,
	description text,
	watchers integer,
	issues integer,
	pull_requests integer,
	is_fork boolean,
	fork_count integer,
	url text,
	primary_language text,
	repository_topics_count integer,
	readme text,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE IF NOT EXISTS repository_topics (
	id integer PRIMARY KEY,
	repository_id integer,
    name text,
    FOREIGN KEY (repository_id) REFERENCES repositories (id)
);

CREATE TABLE IF NOT EXISTS languages (
	id integer PRIMARY KEY,
	repository_id integer,
    name text,
    FOREIGN KEY (repository_id) REFERENCES repositories (id)
);

CREATE TABLE IF NOT EXISTS commit_contributions_by_repository (
	id integer PRIMARY KEY,
	user_id integer,
	total_count integer,
    repository_name text,
    repository_description text,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE IF NOT EXISTS user_log (
	id integer PRIMARY KEY,
	name text,
	login text,
	url text,
	is_processed boolean
);