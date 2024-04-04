<a name="readme-top"></a>


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://git.sbg.ac.at/geo-social-analytics/geo-social-media/tiktok-crawler">
    <img src="img/icon.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">TikTok crawler</h3>

  <p align="center">
    This python script fetches Tiktok posts (videos) based on a user defined query.
    <br />
    <a href="https://git.sbg.ac.at/geo-social-analytics/geo-social-media/tiktok-crawler"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://git.sbg.ac.at/geo-social-analytics/geo-social-media/tiktok-crawler">View Demo</a>
    ·
    <a href="https://git.sbg.ac.at/geo-social-analytics/geo-social-media/tiktok-crawler/-/issues">Report Bug</a>
    ·
    <a href="https://git.sbg.ac.at/geo-social-analytics/geo-social-media/tiktok-crawler/-/issues">Request Feature</a>
  </p>
</div>

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

- python == 3.11.7
- pymongo == 4.6.3
- requests == 2.31.0

>**__Note:__** This set-up is not so complex, so you can just install latest stable realease of python and packages.

### Step 1: Set-up repo

1. Clone the repo.

2. Create a Python environment.

3. Install `requirements.txt` and (potentially) remove package version number.
```
pip install -r requirements.txt
```

### Step 2: Obtain TikTok Research API credentials
Prerequisites for TikTok Research API is that the user is a PhD student or a faculty/research institution memeber. It is not possible to obtain credentials otherwise. It takes a few weeks for Tiktok to provide the neccessary credentials.  

When you obtain the credentials, fill in `config/api-credentials.ini` file with client_id, client_secret, client_key and grant_type. 

### Step 3: Database configuration

#### Option 1 - Recommended Database configuration with .msi installer
1. Visit the [MongoDB download page](https://www.mongodb.com/try/download/community) and download Community Server. 

2. The easiest installation is through Windows installer (msi package), by selecting the "Run Service as Network Service user" option when prompted during the installation process.

3. Optionally, change path to the logs and data folders during the installation.

4. Navigate to the `config` folder and modify the `database.ini` file. Update the `server_path` (default port: 27017, or adjust it in `bin/mongo.cfg` within the MongoDB installation folder) along with the database and collection names.

5. Optionally, but no need for that, change the database name and the collection name. Check [naming restrictions for MongoDB](https://www.mongodb.com/docs/manual/reference/limits/?_ga=2.67582801.1990405345.1706732504-2064098827.1705526269#naming-restrictions).

#### Option 2: Alternative Database configuration with MongoDB binaries (Windows)
Since the Windows .msi distribution needs be installed on the system drive, here are the steps for installing MongoDB binaries which can be installed on the data disk.

1. Visit the [MongoDB download page](https://www.mongodb.com/try/download/community) and choose MongoDB binaries (zip package).

2. Extract the downloaded archive to a location of your choice.

3. Create the following folders at the location of your choice and use them in the next step: 
  - `log` for logging performance of the database and 
  - `data` to store actual data.

4. Launch the command prompt with **administrator privileges**, navigate to the `bin` folder in the directory of extracted MongoDB binaries, and run the following commands to create Windows Service (adjust the paths to `log` and `data` according to your system location):
    ```bash
    mongod --repair 

    mongod --remove 

    mongod --bind_ip  127.0.0.1  --logpath  E:/MongoDBbin/log/mongod.log  --logappend  --dbpath  E:/MongoDBbin/data/db  --port 27017 --serviceName "MongoDB-bin" --serviceDisplayName "MongoDB-bin" --install

    net start MongoDB-b
    ```

5. Check [MongoDB configuration options](https://www.mongodb.com/docs/manual/reference/configuration-options/) to understand the arguments. 

6. Now you can adjust MongoDB service preferences through the Windows Services application.

    > **Note:** This set up of MongoDB binaries excludes an option to configure the port to the server and the path to the data directory in the file `bin/mongo.cfg`, as all configurations have been set through the preceding commands.

7. To finish setting up MongoDB, follow the steps 5 and 6 outlined in the earlier section "Database Configuration (Windows .msi)". 

## Step 4: Define your query

1. Get a bit familiar with Tiktok query options [here](https://developers.tiktok.com/doc/research-api-specs-query-videos/) under *Body* section, key *query*. 

2. Open `config/query-video.ini` and explore the example query.

3. Here is an overview of the query: 
  - Query has operators and, or and not. They are written as config sections. Do not change name of the sections, i.e. keep namings as and_1, and_2, and_3, or_1, or_2, not_1, not_2 etc.
  - *and_*  means to include all the values that fall within those *and_* sections. If you put two *and_* sections, it means that both queries need to be True, in order for a message to be retrieved. If you put two *or_* sections, it means that if either one of those is True, you will retrieve a post. 
  - Furthermore, body of the operators has attributes: operation (IN, EQ, GT...), field_name (a post attribute you want to query) and a field_values (condition that specific field_name needs to meet). 
  - If you want to have only one operator, use *and_1* as a section name and delete all others. Example could be give me all the messages from a specific country(s), thus that is your only condition.
  - These are potential field_names (attributes) of the post that you can define a condtion:  ["create_date", "username", "region_code", "video_id", "hashtag_name", "keyword", "music_id", "effect_id", "video_length"]. 
  - Define start_and end_date as well. 

>**__Note1:__** Please refer to the example query and offical docs to understand it a bit more.
>**__Note2:__** Please also check some videos endpoint reposonse in `raw_server_response/videos.json` to understand field_names better.

## Step 5: Run the script

This script should be run as a scheduled process (for example in Task scheduler in Windows if you use Windows). Therefore, run it at the same time everyday. Reason for this is that we hit rate limits after 20 minutes, and reseting of the rate limits happens every day at 12 AM UTC.

Therefore, just define path to your python interpreter and run `main.py`.

## Tiktok Research API Overview

Disclaimer: After the Telegram experience, I decided to use the word "post" instead of a "video" to refer to tiktok posts, although they officaly call it a "video". 

**Endpoints**

Please refer [here](https://developers.tiktok.com/doc/research-api-codebook/) for all the *objects' endpoints* i.e. attributes of a user or a post under the section 'Query Parameters' for each of the *main* API endpoints. In general, it is possible to query almost everything that is visible in the Tiktok app, except the personal information of the users who are minors or who have made their account private. There are 8 endpoints(user, post, comment...) that further direct to many attributes of a single object. 

For instance: 

  - **user** object endpoints are: display_name, bio_description, avatar_url, is_verified, follower_count, following_count, likes_count, video_count
  - **post** object endpoints are: id,video_description,create_time, region_code,share_count,view_count,like_count,comment_count, music_id,hashtag_names, username,effect_ids,playlist_id,voice_to_text
  - **comment** object endpoints are: id, video_id, text, like_count, reply_count, parent_comment_id, create_time + **important**: we cannot get more than 1000 comments from one post

Furthermore, there are 5 more endpoints: 
  - followers, following, pinned videos, liked videos, reposted videos - these are specific for each user (so we retrieve for instance all videos that are pinned or liked by one user, or all followers of one user).

> **_NOTE:_** We can fetch/filter the data based on many query parameters, such as ["create_date", "username", "region_code", "video_id", "hashtag_name", "keyword", "music_id", "effect_id", "video_length"] for videos, but for users we can do it only based on "user_id". 

**Rate limits**
- Max 100,000 posts and max 100,000 comments per day = 1000 requests with max 100 posts retrieved per request // important: on average 60-70 valid posts out of 100 are retrieved with every request because some posts, although fit our filter, are private or shared by a user that is not 18 (again depends on a user demographics, maybe some topics/queries provide more posts per request)

- 2 million followers/following per day .

- there is no information on rate limits for liked, pinned, reposted and user endpoints. 

- in half an hour we are gonna hit rate limits with fetching posts i.e. in 30 minutes we will try to access 100,000 posts, and retrieve 60-70,000 (more less)

>**_NOTE:_**  We can ask them to increase our rate limits and they will probably do it if we have a valid reason. As stated, we can never get 100 posts per request, as some posts are private.

**Crawling strategy**

> **_NOTE:_** We have decided to make a crawler use case specific. If there are any other ideas, create an issue [here](https://git.sbg.ac.at/geo-social-analytics/geo-social-media/tiktok-crawler/-/issues).

Now, let's explain why we have choosen use case crawl strategy.

TikTok let us access historical data. We cannot be sure that this will be the case forever, but there are some current issues that are stopping us from retrieving data in a real-time manner: 
  - we cannot access tiktok posts for up to 48 hours after they were created,
  - some query parameters (at least likes and view count) are updated every 10 days. 

This means that it is hard to get a posts from a tiktok in the same way you got it from twitter, and it also means that it is hard to use it in the disaster context as we need to **wait as long as 48 hours after the post is shared to retrieve it**, plus we might not be able to get it based on some query paramters because those will not be updated, even after the post is available for retrieval.

Now what I think: 

  - The idea behind their API is for the API user to get the data based on a usecase as we can query based on almost every object's endpoint that exists in their API. Furthermore, I think getting only 100,000 posts and 100,000 comments a day (and 2,000,000 accounts for the user network) is not a huge number, thus I would suggest we create this as a usecase specific, so that we can query based on the needs. 
  - The other option is to have a continous crawl of the posts which means that we could set crawler to every day retrieve 100,000 posts from, at least, two days ago. Daily, there are 34 million new tiktok videos, with who knows how many comments. 

**Proposed project structure/interface** (currently only videos endpoint implemented in this way): 

There are config files for each of the main endpoints (posts,users,followers, following, pinned, liked, reposted, comments,)
  - user defines query criteria and run the script, many query examples will be provided
  - user only defines query, start and end date // example for retrieving posts:
      - query: give me all posts from 1st jan to 7th jan, with one or more of these options ["create_date", "username", "region_code", "video_id", "hashtag_name", "keyword", "music_id", "effect_id", "video_length"]
  - if we want to query users, we can only search based on a **username**, so only username will be provided
  - the same goes for liked videos, reposted videos, pinned videos, followers and following
  - similar for the comments, we provide **post id**

### Questions:

- Are country codes made bsaed on where the user registered the account? Yes, not the country where to post is shared or anything similar
- Explore how keywords work
- https://developers.tiktok.com/doc/research-api-codebook/

<!-- Suggestions and Issues -->
## Feature Requests and Bug Reports

See the [open issues](https://git.sbg.ac.at/geo-social-analytics/geo-social-media/tiktok-crawler/-/issues) for a full list of proposed features and known issues.

If you want this script to fetch more endpoints, please refer to [this page](https://developers.tiktok.com/doc/research-api-codebook/) and explore capabilities of the API.

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* []() Nefta Kanilmaz Umut
* []() Sebastian Schmidt

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Message to Basti and Nefta; comments fetching proposal
Hallo Basti und Nefta, 

I know it is friday evening, but knowing the 35-step authentication process of microsoft, I assume this message will not disturb you. Also, it is not urgent, so don't bother to answer if you are on a vacation. I just wanted to send it here in oreder to not forget. 

The issue: 
  It takes on average 7-10 seconds to fetch comments from a single post. This means it will take 5-7 days to fetch all the comments from posts retrived during 30 minutes crawling period, i.e. all the posts retrieved in one day. This is the reason why I did not want to fetch comments right after we retrieve one post, as this would reduce the number of posts we retrieve. 

  This is why I suggest to separate posts and comments fetching processes. Now, I would propose two options: 
      1. Fetch all the posts 30 minutes a day, and then the rest of the day fetch comments or; 
      2. Do not automatically fetch comments, but when the user decides on it - which promts to two other issues: 
        2.1. Should posts be read from MonogDB? This means we would fetch comments of every post we retrieve or;
        2.2. Should user decide on posts important for them, and then save id of those posts as a list to, for examlpe, a pickle? 

  To wrap this up: 
  We have a trade-off, do we want all the comments, regardless of the time it takes to fetch them? Or, should we filter posts for which we want to fetch comments, thus speed up the process?


  Finally, based on everything, I would suggest next thing: 

    Provide two options: 
      - One option to fetch all the comments from the database
      - One option for a user to provide a list of post ids, and fetch commetns based on that list. 