<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Al's blog</title>

    <link rel="stylesheet" type="text/css" href="font-awesome.min.css">

    <!-- Custom styles -->
    <link rel="stylesheet" type="text/css" href="style.css">

</head>

<body>


<section id="wrapper">
    <header id="header">
        % setdefault('current_page', None)
        <a href="/" class="title {{ 'active' if current_page=='home' else '' }}">Home</a>
        % # <a href="/blog" class="title {{ 'active' if current_page=='blog' else '' }}">Blog</a>
        % # <a href="/projects" class="title {{ 'active' if current_page=='projects' else '' }}">Projects</a>
        <a href="/about" class="title {{ 'active' if current_page=='about' else '' }}">About</a>
    </header>

    {{ !base }}

</section> <!--wrapper-->

    <script type="text/javascript" src="http://code.jquery.com/jquery-1.10.2.js"></script>

</body>
</html>
