Hello everyone,

This is a Stored XSS Lab which I made with my bare knowledge, to teach what is an XSS vulnerability and what you can do with it.

To get started, you need to execute the file and it will create a database file on the directory it presents, so if you want you can create a folder to put the script inside.
After execution of the script, your local website should be active on corresponding (Shows on terminal) IP adresses and ports. You should be able to connect to the website with these IP adresses and ports. If it doesn't work, delete the database file and try again.

****Solution****
1- Click one of the posts.
2- Go to comment section, fill the required areas.
3- Use the payload below on comment space: 
<script>alert("XSS Test")</script>
4- If an alert appears, congratulations you solved the Lab!

That's a Stored XSS, which is your payload is now present in database itself. Causes other users using it will get affected as well.

There is a way too basic way to deal with it. Open the script with a code editor, go to lines 86-87 and remove the comment tags and run your application again, you should delete the database file before running it again.
It now won't allow you to use some characters to prevent an XSS attack.
