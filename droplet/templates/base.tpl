<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Test blog</title>

    <!-- Bootstrap core CSS -->
    <link rel="stylesheet" type="text/css" href="bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="font-awesome.min.css">

    <!-- Custom styles -->
    <link rel="stylesheet" type="text/css" href="style.css">

</head>

<body>

    <div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
        <div class="container">
            <div class="navbar-header">
                <button type="button" class="navbar-toggle" data-toggle="collapse"
                        data-target="#droplet-blog-navbar-collapse">
                    <span class="sr-only">Toggle navigation</span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="http://allanw.co.uk">allanw.co.uk</a>
            </div>
            <div class="navbar-collapse collapse" id="droplet-blog-navbar-collapse">
                <ul class="nav navbar-nav">
                    <li class="active"><a href="/">Home</a>
                    </li>
                    <li class=""><a href="/about">About</a>
                    </li>
                </ul>
            </div> <!-- .nav-collapse -->
        </div> <!-- .container -->
    </div> <!-- .navbar -->

    <div class="container">
        <div class="row">
            <div class="col-sm-9">
                <ul>
                    {{ !base }}
                </ul>
            </div>

            <div class="col-sm-3 well well-sm" id="sidebar">
                <h4>About</h4>
                <p>I'm Allan Whatmough, a web developer based in London, U.K.</p>

                <h4>Elsewhere</h4>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item">
                      <ul class="list-group" id="social">
                        <li class="list-group-item"><a href="http://twitter.com/allanw"><i class="fa fa-twitter-square fa-lg"></i> twitter</a></li>
                        <li class="list-group-item"><a href="http://www.linkedin.com/in/allanwhatmough"><i class="fa fa-linkedin-square fa-lg"></i> linkedin</a></li>
                        <li class="list-group-item"><a href="http://github.com/allanw"><i class="fa fa-github-square fa-lg"></i> github</a></li>
                      </ul>
                    </li>
                </ul>

            </div>
        </div>
    </div>


    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script type="text/javascript" src="http://code.jquery.com/jquery-1.10.2.js"></script>
    <script src="bootstrap.min.js"></script>

</body>
</html>