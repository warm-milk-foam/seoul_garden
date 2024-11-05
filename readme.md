# Seoul Garden Project 
Students of AWS Accelerator 2024  
By Ingo, Liu JunHao, Samuel Koh, Gabriel Tang, Mikail Jnr and Jeniece Tham  

This respository is the code we wrote for the Seoul Garden challenge statement  

To run the experience, clone the repository and run the app.py file with  
```
python3 app.py
```
to the start the Flask application.  

Credits to:
1) Seoul Garden for food images (ONLY FOR REFERENCE) to simulate the experience.  
2) AWS Accelerator mentors, who gave us this challenge statement have guided us in the making of the project  
3) And you, for bothering to read this.  
4) ~~Mistral, ChatGPT and Phind, the reason why the code is present right now~~

# Features
The Flask project attempts to simulate an experience ordering food from a restaurant with an AI chatbot.  
DISCLAIMER: This is just a local project and WILL NOT have real functionality in ordering actual food. It can only be accessed by the person running it and will be inaccessible to others on the internet.  
  
The project aims to automate:  
1) Create and authenticate accounts 
2) Use an AI model to promote and recommend deals, using information from order histories
3) Order food online(?)  
5) All the data is persistent so the chatbot will still remember your information after finishing orders!

# Requirements
Dependencies, ibraries and other stuff to be installed so that the project can run  
(I should add this into a requirements.txt file)  
1) Ollama, specifically using llama3.2:latest with a size of 2.0 GB  
2) Flask and its own modules, request, render_template, redirect, url_for, flash, session, jsonify  
3) Other modules such as os, uuid, datetime library, and subprocess
4) Python3