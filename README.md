# LSC-Scraper-AWS
Final project for Large Scale Computing
README:
Contents:
•	Lambda Layer: AO3-Linux zipped folder
•	Lambda Code AND Layer in AWS Deployment Package: scraper_1 zip file
•	Local script used to invoke and parallelize lambda: main.py


My intention with this project was to find a way to collect data which would aid in a study on the fanfiction website Archive Of Our Own. 
The study I was intending to run was my final project for my Social Network Analysis course, though I had to scale back some aspects of this project, 
largely due to bugs in the unofficial API I utilized, which made the data unsuitable for the original purpose.

The project (that I would have done if it weren’t for issues with the API):
Social Network Analysis is a field which analyzes networks. A fanfiction website such as Archive Of Our Own contains many user-uploaded works, 
as well as many user profiles. Users can write works, as well as bookmark other users works. Looking at these connections between authors and users, 
they can be thought of as edges in a network. If this information is stored in an author by work matrix, it can be transposed and multiplied by itself to find a work 
by work adjacency matrix. The information in this matrix shows which works are connected to each other through authors. 
I would analyze this data to try to construct subgroups and identify which traits of works are likely to be linked with different cultural subgroups.

Issues with the API:
As the API for Archive Of Our Own (ao3_api) was unofficial, I was unable to collect data in line with my original intended scope. 
One issue was with the bookmark collection tool. The API was able to successfully count how many stories a given author had bookmarked, 
however it was unable to load them as works or display their titles. This was odd, as the API was able to accomplish this task for the works written by the author. 
For time and scope reasons, I elected to scale down my data collection to simply collect works the author had written rather than fix the API. 
The second issue rendered the first obsolete. The API didn’t actually interface successfully with the website in some essential ways. 
Particularly, on Archive Of Our Own, authors have the option to choose a pseudonym, or nickname. When scraping the author of a particular work, 
the api treated this pseudonym as the author’s actual username. This resulted in many instances where after collecting a given list of authors from different works, 
the API was unable to access those author’s profile pages. 
Instead, it attempted to access a non-existent profile page that would belong to a user who had the author’s pseudonym as their username. 

Due to these issues the data I elected not to collect any information related to the author. Instead, for each work I scraped the following information:
•	The identification number of said work
•	The number of chapters contained in the work
•	The number of words contained in the work
•	The number of hits (times the work was viewed) of the work
•	The rating of the work
o	This rating is a string which signals which audiences the work is appropriate for: much like movie ratings

I had a three step process to scrape the data and store it in a dynamodb table.
The first step was constructing the table. I elected to do it manually, and navigated to the dynamodb section on AWS. 
I then created a standard dynamodb table named ‘ao3_work_table’, in which I stored my results. I elected to use dynamodb for two reasons. 
The first is that it scales extremely well. For the purposes of this project I scraped the works of the fandom ‘The Good Place (TV)’. 
If I were inclined to scrape more data, such as all of Archive Of Our Own, I would be able to store it in a dynamodb. 
Secondly, dynamodb emphasizes availability, I don’t have to worry about losing access to part of the dataset. This allows for many concurrent reads and writes. 
I only requested 5 write units as I was working with a relatively small dataset, but if I were to scale it up I could have requested more. 
The scalability of the writes is very important, as I would be parallelizing my input.

	I split up the actual system into two pieces. One is the lambda which actually stores the requisite information.
  The other is my parallelization component. Archive Of Our Own blocks an IP address when it visits pages too quickly in order to prevent DDOS attacks. 
  One can scrape data without being blocked by only making a request once every four seconds. That doesn’t scale very well: 
  collecting information on 300,000 stories would take about 5 months at that rate!
  
	I will describe what my Lambda function does before I discuss how I implemented the parallelization. 
  As I previously mentioned, the API that I found allows one to search Archive Of Our Own, filtering by a wide selection of criteria. 
  The search function can only observe one page of the results at a time however, and each page contains up to 20 entries. 
  What my lambda function does is that first it checks to see if my dynamodb table exists and is ready to input. The function has as inputs the fandom to search, 
  in this case ‘The Good Place (TV)’, as well as a specific page number. It then searches that page. For each work on that page, 
  it scrapes the relevant data and pushes it into my dynamodb table, using the unique work_id tag as the work’s partition key.
  
	In order to get the ao3_api package working on the AWS Lambda system, I installed the package into an empty folder. 
  I then zipped this folder and uploaded it as a Lambda Layer, which I bound to my scraper lambda function. 
  The primary challenge of this is that when installing the package into the folder, it installed the windows versions of the package as I am on a windows system. 
  However, AWS runs on linux. This was solved by having Professor Clindaniel perform the package installation, sending the folder to me.
  
	AWS Lambda functions come with a sort of parallelization: each time a Lambda is called it creates an instance of said function. 
  If the function is called again while it is still running, Lambda creates another instance of the same function and runs them concurrently. 
  These don’t connect to Archive Of Our Own from the same IP address, so there are no issues with blockages. By default AWS can run up to 1000 instances of Lambda at once. 
  In the US East region in which I’m working, it can temporarily run up to 3000 instances. That’s very effective scaling, 
  though more than what I need for this specific use-case.
  
	I used mpi4py on my local machine to handle the parallelization. For this project I used five ranks. 
  First I ran the ao3 search on “The Good Place (TV)” in order to tell how many pages it had. Following that, I divided the pages between the five ranks. 
  Each rank was charged with invoking each of its page numbers to ‘scraper_1’, the lambda function which I used. 
  I used the invocation type request response because Lambda can hold up to 600 functions in a queue to run asynchronously. 
  While I wouldn’t be requesting more than that number of pages to run simultaneously, that runs the risk of failing to scale properly. 
  Therefore I used the synchronous approach to guarantee that each page is hit.  That’s my project!

