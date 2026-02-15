## Description
- My Flask backend has a /get-data endpoint (doesn't take in any parameters) which parses a google doc with my reading list using the Google Docs API. My readings are listen in a format like: "Underrated Reasons to Be Thankful II | Themes: #gratitude, #culture, #essay" and it returns a JSON file with a list of articles (before the | symbol) and the hashtags (after the | symbol).
- When a user clicks "Draw", the frontend calls the /get-data endpoint with the selected theme and stores a list of the readings with that hashtag. Then it randomly picks one. 
- All secret keys are stored on Render server, and not on Github (hopefully)

## Prompts
- i would like to make a website to connect to a python service on render.com that uses the google docs API. i want to make a project that takes a google doc full of links to articles i've read and gives one to the user. maybe the user has the option to get a random one or they can pick a theme / vibe to get a link from that. each reading can have multiple relevant themes / vibes. help me do this. i already have the API enabled, here is the spec on the google doc API:(*copy pasted code*)
- can you take this UI (*copy pasted code*) and combine it with this content (*copy pasted code*)
- the links are linked on the article titles. is there any way they can extract the link?
- the background is good and i am able to click the button. however, it always says "nothing found" 
- how can i change my google doc to make it easier to process
