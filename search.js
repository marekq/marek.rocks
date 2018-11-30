<center>
<input type="text" id="page" value="">
<input type="submit" id="box" onkeypress="goToPage();" onclick="goToPage();">
</center><br>

<script type="text/javascript">
    function goToPage() {
        var page = document.getElementById('page').value;
        window.location = "https://marek.rocks/tag/" + page;
    }
</script>

<script>
var input = document.getElementById("page");
input.addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        document.getElementById("box").click();
    }
});
</script>