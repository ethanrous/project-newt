    
    var selectedRow = null;
   
    function onFormSubmit(e){
        event.preventDefault();
        var formData = readFormData();
        if (selectedRow == null){
            insertNewItem(formData);
        }
        else{
            updateItem(formData);
        }
        resetForm();
    }

    function readFormData(){
        var formData= {};
        formData["item"] = document.getElementById("item").value.toUpperCase();
        formData["quantityValue"] = document.getElementById("quantityValue").value + " " + document.getElementById("quantityType").value;
        formData["expiration"] = document.getElementById("expiration").value;
        formData["location"] = document.getElementById("location").value;
        return formData;
    }

    function insertNewItem(data){
        var table = document.getElementById("storeList-fridge").getElementsByTagName('tbody')[0];
        var newRow = table.insertRow(table.length);
        var cell1 = newRow.insertCell(0);
            cell1.innerHTML = data.quantityValue;
        var cell2 = newRow.insertCell(1);
            cell2.innerHTML = data.item;
        var cell3 = newRow.insertCell(2);
            cell3.innerHTML = data.expiration;
        var cell4 = newRow.insertCell(3);
            cell4.innerHTML = '<button onClick="onEdit(this)">Edit</button> <button onClick="onDelete(this)">Delete</button>'
    }

    function onEdit(td){
        selectedRow = td.parentElement.parentElement;
        document.getElementById("quantityValue").value = selectedRow.cells[0].innerHTML;
        document.getElementById("item").value = selectedRow.cells[1].innerHTML;
        document.getElementById("expiration").value = selectedRow.cells[2].innerHTML;
    }

    function updateItem(formData){
        selectedRow.cells[0].innerHTML = formData.quantityValue;
        selectedRow.cells[1].innerHTML = formData.item;
        selectedRow.cells[2].innerHTML = formData.expiration;
    }

    function onDelete(td) {
        if (confirm('Do you want to delete this item?')) {
            row = td.parentElement.parentElement;
            document.getElementById('storeList-fridge').deleteRow(row.rowIndex);
            resetForm();
        }
    }

    function resetForm() {
        document.getElementById("quantityValue").value = '';
        document.getElementById("quantityType").value = "";
        document.getElementById("item").value = '';
        document.getElementById("expiration").value = '';
        document.getElementById("location").value = "";

        selectedRow = null;
    }

