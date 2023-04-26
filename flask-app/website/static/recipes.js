//import { recipe_key } from "./config.js"

function buildRecipe(recipeObj){
    let imgUrl = recipeObj.image
    let nameStr = recipeObj.label
    let ingridientsArr = recipeObj.ingredientLines
    let timeInt = recipeObj.totalTime
    let url = recipeObj.url

    if (timeInt === 0){
        timeInt = "Unknown"
    }else{
        timeInt = `${timeInt}` + " Minutes"
    }

    let cardStr = `
    <div class="card m-3 " style="max-width: 45vw;">
        <div class="row g-0">
            <div class="col-md-4">
                <img
                src="${imgUrl}"
                alt="Trendy Pants and Shoes"
                class="img-fluid rounded-start"
                />
            </div>
            <div class="col-md-8">
                <div class="card-body">
                    <h5 class="card-title"><a href="${url}" target="_blank" rel="noopener noreferrer">${nameStr}</a></h5>
                    <h6 class="card-subtitle mb-2 text-muted">
                        Cook Time: ${timeInt}
                    </h6>
                    <h6 class="card-subtitle mb-2 text-muted">
                    Ingridients:
                    </h6>

                    <ul class="list-group list-group-horizontal position-relative overflow-auto w-100"></ul></div></div></div></div>`

    let cardContainer = document.createElement('div')
    cardContainer.innerHTML = cardStr
    let card = cardContainer.lastChild
    let cardBody = card.lastChild.lastChild.lastChild.lastChild
    let str = ``
    ingridientsArr.map(ingridient => {
        ingridient = ingridient.toLowerCase();
        ingridient = ingridient.replace(/\d+/g, '')
        ingridient = ingridient.replace("-", '')
        ingridient = ingridient.replace("/", '')
        ingridient = ingridient.replace(".", '')

        // ingridient = ingridient.replace("tsp", '')
        // ingridient = ingridient.replace("lbs", '')
        // ingridient = ingridient.replace("tbs", '')
        // ingridient = ingridient.replace("cup", '')
        // ingridient = ingridient.replace("pound", '')
        // ingridient = ingridient.replace("cups", '')
        // ingridient = ingridient.replace("pounds", '')
        // ingridient = ingridient.replace(" g ", '')
        // ingridient = ingridient.replace("g ", '')
        // ingridient = ingridient.replace("grams", '')
        // ingridient = ingridient.replace("kg", '')
        // ingridient = ingridient.replace("tablespoons", '')
        // ingridient = ingridient.replace("tbsp", '')
        // ingridient = ingridient.replace("oz", '')
        // ingridient = ingridient.replace("ounces", '')
        // ingridient = ingridient.replace("teaspoon", '')
        // ingridient = ingridient.replace("tablespoon", '')
        // ingridient = ingridient.replace("ml", '')
        

        if (ingridient.length > 28){
            ingridient = ingridient.slice(0,28) + "[...]"
        }
        let ing = `<li class="list-group-item" style="width: 200rem">${ingridient}</li>`
        str = str + ing
    })
    cardBody.innerHTML = cardBody.innerHTML+str


    return cardContainer
}

function addRecipe(recipeObj){
    let cardContainer = buildRecipe(recipeObj)
    let recipeLst = document.getElementById("container")
    let card = cardContainer.lastChild
    let li = document.createElement('div')
    li.appendChild(card)
    recipeLst.appendChild(li)
}




async function fetchRecipes(){
    const recipeInput = document.getElementById('recipe-input')
    let recipeLst = document.getElementById("container")
    recipeLst.innerHTML = ''
    let keywords = recipeInput.value
    const url = `https://edamam-recipe-search.p.rapidapi.com/search?q=${keywords}`;
    const options = {
        method: 'GET',
        headers: {
            'content-type': 'application/octet-stream',
            'X-RapidAPI-Key': "",
            'X-RapidAPI-Host': 'edamam-recipe-search.p.rapidapi.com'
        }
    };

    try {
        const response = await fetch(url, options);
        const result = await response.text();
        let res = JSON.parse(result)
        console.log(res)
        for (let i = 0; i < res.hits.length; i++){
            addRecipe(res.hits[i].recipe)
            
        }
    } catch (error) {
        console.error(error);
    }
}

// function fetch_test(){
//     fetch('fetchtest').then(response => response.json()).then(function(data){
//         document.getElementById("to_change").innerHTML = data['some text']
//     })
// }