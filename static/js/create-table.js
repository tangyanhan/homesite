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

// Strip format specifiers in header
function splitHeaders(headers) {
    newHeaders = new Array()
    functions = new Array()
    types = new Array()
    var pattern = /(.*)\[(.*)\]/
    for( var i=0; i<headers.length; i++ ) {
        field = headers[i]
        var match = pattern.exec(field)
        var type = ""
        func = null
        if(match) {
            field = match[1]
            type = match[2]
            var optionPattern = /options\((.*)\)/
            match = optionPattern.exec(type)
            choices = ""
            if( match ) {
                options = match[1].split("|")
                func = function(cell, cellData, type){
                    select = document.createElement("select")
                    for(var iOption=0; iOption<options.length; iOption++) {
                        option = document.createElement("option")
                        option.value = iOption
                        option.innerHTML = options[iOption]
                        if(cellData == iOption) {
                            option.setAttribute("selected", "selected")
                        }
                        select.append(option)
                    }
                    cell.append(select)
                    return select
                }
            }else{
                func = function(cell, cellData, type) {
                    input = document.createElement("input")
                    input.type = type
                    input.value = cellData
                    cell.append(input)
                    return input
                }
            }

        }
        types.push(type)
        newHeaders.push(field)
        functions.push(func)
    }
    return {
        'types': types,
        'headers': newHeaders,
        'functions': functions
    }
}