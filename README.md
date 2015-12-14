# Appie

Appie is a simple static generator for websites. Just point it to a 
directory and it will provide you with a json file with all of its 
contents and a static directory with all static files.

Appie parses files thourgh extensions. Extensions are very easy to 
write. If a file or directory is not matched to an extension it will be 
copied to the target build directory.

## Extensions

The following extensions are available:

- \_\*: any file starting with an \_ will be loaded into the json
- \*.textile: html text entry in the resulting json file
- \*.png: converted to a thumbnail jpg (filename_thumb.jpg) and a jpg with a fixed dimension (filename.jpg)

Extensions being worked on:

- _rd_*: directories starting with _rd_ will be parsed into an academic 
style paper

## Example

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
Appie is run as follows:
```
$ appie -s /path/to/directory
```
You will then have a new directory 'build' in your current direcyory 
with the following contents:
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
  "files": {"report2010.pdf": "/files", "report2009.pdf": "/files", "report2008.pdf": "/files"}
  "img" : { "banner": { "src": "banner.png", "thumb" : "banner_thumb.jpg", "web": "banner.jpg", }}
}
```
If you run appie with the -w flag it will serve the generated files through 
a HTTP server. By default this HTTP server runs on port 8000.
```
$ appie -s /path/to/directory -w
Serving on port 8000...     press CTRL-C to quit
```

## About ##

Appie originated at the [z25 Foundation](http://www.z25.org) where it is 
used to manage the main website. All content of the website is 
automatically updated through the subversion repositories of z25's 
projects by Appie.
