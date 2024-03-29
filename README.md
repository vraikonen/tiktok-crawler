<a name="readme-top"></a>


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://git.sbg.ac.at/geo-social-analytics/geo-social-media/tiktok-crawler">
    <img src="img/icon.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Ongoing project for a TikTok crawler.</h3>

  <p align="center">
    This is an ongoing project for crawling tiktok. Current discussion: endpoints, crawling strategy, rate limits, user-network
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

## Current tasks:

Concrete, overall tasks proposed by Basti:

Find out whether it is possible to tag locations on TikTok
Check out the TikTok API documentation and figure out the following:
  - What kind of information can we get?

  - What is the best way to filter data for specific use cases (i.e. based on timeframe, keywords, locations)? What would be the best crawling strategy?

  - Which rate limits exist?

  - Can you get information about user networks?

## API Overview

Disclaimer: After the Telegram experience, I decided to use the word "post" instead of a "video" to refer to tiktok posts, although they officaly call it a "video". 

**Endpoints**

Please refer [here](https://developers.tiktok.com/doc/research-api-codebook/) for all the *objects' endpoints* i.e. attributes of a user or a post under the section 'Query Parameters' for each of the *main* API endpoints. In general, it is possible to query almost everything that is visible in the Tiktok app, except the personal information of the users who are minors or who have made their account private. There are 8 *main* endpoints(user, post, comment...) that further direct to *objects'endpoints* i.e. attributes of a single object. 

For instance: 

  - **user** object endpoints are: display_name, bio_description, avatar_url, is_verified, follower_count, following_count, likes_count, video_count
  - **post** object endpoints are: id,video_description,create_time, region_code,share_count,view_count,like_count,comment_count, music_id,hashtag_names, username,effect_ids,playlist_id,voice_to_text
  - **comment** object endpoints are: id, video_id, text, like_count, reply_count, parent_comment_id, create_time + **important**: we cannot get more than 1000 comments from one post

Furthermore, there are 5 more *main* endpoints: 
  - followers, following, pinned videos, liked videos, reposted videos - these are specific for each user (so we retrieve for instance all videos that are pinned or liked by one user, or all followers of one user).

> **_NOTE:_** We can fetch/filter the data based on many query parameters, such as ["create_date", "username", "region_code", "video_id", "hashtag_name", "keyword", "music_id", "effect_id", "video_length"] for videos, but for users we can do it only based on "user_id". 

**Rate limits**
- Max 100,000 posts and max 100,000 comments per day = 1000 requests with max 100 posts retrieved per request // important: on average 60-70 valid posts out of 100 are retrieved with every request because some posts, although fit our filter, are private or shared by a user that is not 18 (again depends on a user demographics, maybe some topics/queries provide more posts per request)

- 2 million followers/following per day .

- there is no information on rate limits for liked, pinned, reposted and user endpoints. 

- in half an hour we are gonna hit rate limits with fetching posts i.e. in 30 minutes we will try to access 100,000 posts, and retrieve 60-70,000 (more less)

> **_NOTE:_**  We can ask them to increase our rate limits and they will probably do it if we have a valid reason.

> **_NOTE2:_**  As stated, we can never get 100 posts per request, as some posts are private.

**Crawling strategy discussion**

> **_NOTE:_** We have decided to make a crawler use case specific. If there are any other ideas, create an issue [here](https://git.sbg.ac.at/geo-social-analytics/geo-social-media/tiktok-crawler/-/issues).

Now, let's explain why we have choosen use case crawl strategy.

TikTok let us access historical data. We cannot be sure that this will be the case forever, but there are some current issues that are stopping us from retrieving data in a real-time manner: 
  - we cannot access tiktok posts for up to 48 hours after they were created,
  - some query parameters (at least likes and view count) are updated every 10 days. 

This means that it is hard to get a posts from a tiktok in the same way you got it from twitter, and it also means that it is hard to use it in the disaster context as we need to **wait as long as 48 hours after the post is shared to retrieve it**, plus we might not be able to get it based on some query paramters because those will not be updated, even after the post is available for retrieval.

Now what I think: 

  - The idea behind their API is for the API user to get the data based on a usecase as we can query based on almost every object's endpoint that exists in their API. Furthermore, I think getting only 100,000 posts and 100,000 comments a day (and 2,000,000 accounts for the user network) is not a huge number, thus I would suggest we create this as a usecase specific, so that we can query based on the needs. 
  - The other option is to have a continous crawl of the posts which means that we could set crawler to every day retrieve 100,000 posts from, at least, two days ago. Daily, there are 34 million new tiktok videos, with who knows how many comments. 

**Proposed project structure/interface** (if we accept project-specific crawling strategy?): 

There are config files for each of the main endpoints (posts,users,followers, following, pinned, liked, reposted, comments,)
  - user defines query criteria and run the script, many query examples will be provided
  - user only defines query, start and end date // example for retrieving posts:
      - query: give me all posts from 1st jan to 7th jan, with one or more of these options ["create_date", "username", "region_code", "video_id", "hashtag_name", "keyword", "music_id", "effect_id", "video_length"]
  - if we want to query users, we can only search based on a **username**, so only username will be provided
  - the same goes for liked videos, reposted videos, pinned videos, followers and following
  - similar for the comments, we provide **post id**


### TODO

- Check what happens with pagination if the script is terminated? add retry if there is an error but will we then be able to use search_id once again? check if there is retry in the requests library
- Check what happens when we hit rate limits: will it be able to use the cursor and search_id values from the last day?
- Save all response keys besides "videos" in the MongoDB and read it from there, no damn pickle
- Add stop to stop the script after some time if someone wants to explore the data. or not
- Check how often should we create token?
- Check other docs not specific for research api, there might be a lot of things that are the same, such as here https://developers.tiktok.com/doc/tiktok-api-v2-error-handling/
- find rate limits for other endpoints 
- Are country codes made bsaed on where the user stated is from?
- Explore how keywords work
- CALL IT ATTRIBUTES AND ENDPOINTS, not main endpoints and objects endpoints?! Wtf

### Explanation

Comments takes a lot of time to fetch, therefore you need to do it separately! Why?!
Because fetching all the comments from all the posts retrieved in 30 minutes will take 48hours
It takes on average 7-10 seconds to fetch comments of a post, therefore to fetch all the comments from all the posts retrieved in a day, it will take 5-7 days

<p align="right">(<a href="#readme-top">back to top</a>)</p>
