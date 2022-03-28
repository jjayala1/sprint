function myFunc(vars) {
    return vars
}


function graph(dataset){

    let labels = [];
    let likes = [];
    let comments = [];

    for(d of dataset){
        labels.push(d[0]);
        likes.push(d[1]);
        comments.push(d[2]);
    }



    new Chart(document.getElementById("postsChart"), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Likes",
                    backgroundColor: ["#0e6e02"],
                    data: likes
                },
                {
                    label: "Comments",
                    backgroundColor: ["#045850"],
                    data: comments
                },

            ]
        },
        options: {
            legend: { display: true },
            plugins: {
                title: {
                    display: true,
                    text: 'Sprint'
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Day/Sprinter'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: ''
                    }
                }
            },
        }
    });
}
