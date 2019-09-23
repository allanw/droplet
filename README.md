A simple Dropbox-based blog generator built using Bottle.

It uses:

- Bottle framework for routing/templating
- Redis for caching
- pandoc and wkhtmltopdf (both need to be installed to test some features locally)

N.B. Tested with Pandoc version 1.16. Later versions (2.0+) don't currently work with the code to generate .txt version of the HTML as-is (will need some modifications).

## Heroku buildpack

`$ heroku buildpacks --app allanwblog`
```
allanwblog Buildpack URL
https://github.com/allanw/heroku-buildpack-multi.git
```
