function getAddItems(){
    var item = document.getElementById('item').value;
    var quantity = document.getElementById('quantityValue').value;
    var quantityType = document.getElementById('quantityType').value;
    var expirationdate = document.getElementById('expiration-date').value;
    var location = document.getElementById('location').value;

    const node = document.createElement('li');

    node.innerText =  quantity + " " + quantityType + " " + item + " Expires:" + expirationdate;

    // if (location == "fridge"){
    //     document.getElementById("fridge-section").appendChild(node)
    // }
    // if (location == "fridge-door"){
    //     document.getElementById("fridge-door").appendChild(node)
    // }
    // if (location == "freezer"){
    //     document.getElementById("freezer").appendChild(node)
    // }
    // if (location == "freezer-door"){
    //     document.getElementById("freezer-door").appendChild(node)
    // }
}