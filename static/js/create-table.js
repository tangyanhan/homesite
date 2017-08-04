// Create table under node parent, with headers and data
// @param: customizeRow(row, rowIdx, rowData)
// @param: customizeCell(rowIdx, colIdx, cell, cellData)
function createTable(parent, headers, data, customizeRow, customizeCell)
{
    table = document.createElement("table")
    parent.empty()
    parent.append(table)
    table.classList.add("table")
    table.classList.add("table-hover")

    thead = document.createElement("thead")
    table.append(thead)

    tableHeader = document.createElement("tr")
    thead.append(tableHeader)
    tableHeader.innerHTML = ""
    // Add selection column
    th = createCheckboxElement("th")
    input = th.getElementsByClassName("checkbox")[0]
    input.classList.add("check-all")
    tableHeader.append(th)
    // Listen to click event
    $(".check-all").click(function(){
        var checked = $(this).attr("checked")
        if( typeof(checked) == 'undefined' ) {
            $("input[type='checkbox']").attr("checked", true);
        }else{
            $("input[type='checkbox']").attr("checked", false);
        }
    });

    for(var i=0; i<headers.length; i++) {
        h = headers[i]
        th = document.createElement("th")
        th.innerHTML = h
        tableHeader.append(th)
    }

    tableBody = document.createElement("tbody")
    table.append(tableBody)
    tableBody.innerHTML = ""
    for(var i=0; i<data.length; i++) {
        row = data[i]
        tr = document.createElement("tr")
        td = createCheckboxElement("td")
        tr.append(td)
        for(var j=0; j<row.length; j++){
            cellData = row[j]
            td = document.createElement("td")
            td.innerHTML = cellData
            customizeCell(i, j, td, cellData)
            tr.append(td)
        }
        customizeRow(tr, i, row)
        tableBody.append(tr)
    }
}

function createCheckboxElement(type) {
    element = document.createElement("th")
    element.innerHTML = '<input type="checkbox" class="checkbox">'
    return element
}