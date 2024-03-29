
<h1 align="center">Alexa Skill: Illini Bus</h1>
<p align="center"> A voice-activated way for finding the next buses coming to your Urbana-Champaign bus stop </p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#demo">Demo</a> •
  <a href="#components">Components</a> •
   <a href="#resources">Resources</a>
</p>

<div align="center">

<!-- <br> -->

[![license](https://img.shields.io/github/license/dec0dOS/amazing-github-template.svg?style=flat-square)](LICENSE)

</div>

## Features

- Say `open illini bus` to start the skill

- Say key word `use` then the name of your bus stop
    - Example: `use [bus stop name]`
    - Implemented using the [CUMTD Auto Complete API](https://developer.cumtd.com/documentation/autocomplete/v1.0.0/stop/)

- Uses DynamoDB to remember your bus stop
    - Faster future responses

- Hosted on AWS Lambda


## Demo
<p align="center"><img src="https://github.com/3sannasia/Alexa-Illini-Bus/assets/54860072/c8548a84-b6af-457e-a523-6ef491f5e0a7"width="400" /></p>



## Resources
- [Alexa Skills Kit SDK](https://developer.amazon.com/en-US/docs/alexa/alexa-skills-kit-sdk-for-python/overview.html)
- [DynamoDB for Data Persistence](https://developer.amazon.com/en-US/docs/alexa/hosted-skills/alexa-hosted-skills-session-persistence.html)
- [Champaign-Urbana Mass Transit District API](https://developer.cumtd.com)


