function buildRecipe(recipeObj){
    let imgUrl = recipeObj.image
    let nameStr = recipeObj.label
    let ingredientsArr = recipeObj.ingredientLines
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
                    ingredients:
                    </h6>

                    <ul class="list-group list-group-horizontal position-relative overflow-auto w-100"></ul></div></div></div></div>`

    let cardContainer = document.createElement('div')
    cardContainer.innerHTML = cardStr
    let card = cardContainer.lastChild
    let cardBody = card.lastChild.lastChild.lastChild.lastChild
    let str = ``
    ingredientsArr.map(ingredient => {
        ingredient = ingredient.toLowerCase();
        ingredient = ingredient.replace(/\d+/g, '')
        ingredient = ingredient.replace("-", '')
        ingredient = ingredient.replace("/", '')
        ingredient = ingredient.replace(".", '')

        // ingredient = ingredient.replace("tsp", '')
        // ingredient = ingredient.replace("lbs", '')
        // ingredient = ingredient.replace("tbs", '')
        // ingredient = ingredient.replace("cup", '')
        // ingredient = ingredient.replace("pound", '')
        // ingredient = ingredient.replace("cups", '')
        // ingredient = ingredient.replace("pounds", '')
        // ingredient = ingredient.replace(" g ", '')
        // ingredient = ingredient.replace("g ", '')
        // ingredient = ingredient.replace("grams", '')
        // ingredient = ingredient.replace("kg", '')
        // ingredient = ingredient.replace("tablespoons", '')
        // ingredient = ingredient.replace("tbsp", '')
        // ingredient = ingredient.replace("oz", '')
        // ingredient = ingredient.replace("ounces", '')
        // ingredient = ingredient.replace("teaspoon", '')
        // ingredient = ingredient.replace("tablespoon", '')
        // ingredient = ingredient.replace("ml", '')


        if (ingredient.length > 28){
            ingredient = ingredient.slice(0,28) + "[...]"
        }
        let ing = `<li class="list-group-item" style="width: 200rem">${ingredient}</li>`
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
            'X-RapidAPI-Key': recipeKey,
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