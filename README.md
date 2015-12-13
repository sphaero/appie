# appie

Appie is a simple static generator for websites. Just point it to a directory and it will provide you with a json file with all of its contents and a static directory with all static files.

Appie parses files with no extensions but starting with a '_'(underscore) or with extensions which are added to appie as modules.

## Modules ## 

By default the following file extensions are parsed:

- .textile > html text entry in the resulting json file
- .png > converted to a thumbnail jpg (filename_thumb.jpg) and a jpg with a fixed dimension (filename.jpg)

Currently there are the following modules

- R&D: A module which creates a html document in a acacdemic style paper. R&D entries are based on a directory name starting with '_rd_'

## Example ##
For example we have the following directory contents:
```
./files
./files/report_2008.pdf
./files/report_2009.pdf
./files/report_2010.pdf
about.textile
home.textile
./img/banner.png
````
Appie is then run as follows from this directory:
```
appie.py
```
You will then have a new directory 'build' with the following contents:
```
./build/files/report_2008.pdf
./build/files/report_2009.pdf
./build/files/report_2010.pdf
./build/img/banner_thumb.jpg
./build/img/banner.jpg
./build/img/banner.png
./build/all.json
```
The file 'all.json' will contain:
```
{ "home.textile" : "<h3>Test</h3><p>This is just a test</p>",
  "about.textile" : "<h3>About</h3><p>What about it</p>",
  "files" : [ "report_2008.pdf", "report_2009.pdf", "report_2010.pdf" ],
  "img" : { "banner": { "src": "banner.png", "thumb" : "banner_thumb.jpg", "web": "banner.jpg" }}
}
```

## About ##

Appie originated at the "z25 Foundation":http://www.z25.org where it is 
used to manage the main website. All content of the website is automatcally
updated through the subversion repositories of z25's projects.
