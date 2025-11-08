$(document).ready(function () {
    // debugger
    const matches = document.getElementsByClassName("avatarButton");
    // console.log(matches.length)

    for (let i = 0; i < matches.length; i++) {

        matches[i].addEventListener('click', function () {
            //debugger
            console.log("Inside");
            console.log(document.getElementById("img" + matches[i].id).src);

            $.ajax({
                type: 'POST',
                url: '/chooseAvatar',
                contentType: "application/json",
                data: JSON.stringify({ path: document.getElementById("img" + matches[i].id).src }),
                error: function () {
                    alert("Error");
                },
                success: function (data, status, xhr) {
                    console.log(data['path']);
                    console.log('Success!');

                    $("#userAvatar").attr('src', data['path']);
                }
            });
        });
    };
});
