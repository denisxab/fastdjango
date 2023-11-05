document.addEventListener("DOMContentLoaded", async () => {
    const url_host = "http://localhost:8000";
    const url_list_models = `${url_host}/admin/models`;
    const url_list_rows_model = `${url_host}/admin/rows`;
    const url_list_row_model_from_pk = `${url_host}/admin/row/`;

    const modelsList = document.getElementById("models");
    const recordsList = document.getElementById("recordsTable");
    const backButton = document.getElementById("backButton");
    const deleteRowButton = document.getElementById("deleteRowButton");
    const recordsHeader = document.getElementById("recordsHeader");

    let currentRecordsData, currentModel, currentRowPk;

    const fetchData = async (url) => (await fetch(url)).json();
    const deleteData = async (url) => (await fetch(url, { method: "DELETE" })).json();

    const renderModelsList = (modelsData) => {
        modelsData.forEach((model) => {
            const listItem = document.createElement("li");
            listItem.innerText = model.name;
            listItem.addEventListener("click", async () => {
                currentModel = model.name;
                renderRecordsTable(await fetchData(`${url_list_rows_model}?model=${model.name}`), model.name);
            });
            modelsList.appendChild(listItem);
        });
    };

    const renderRecordsTable = (recordsData, model) => {
        recordsList.innerHTML = "";

        if (recordsData.length > 0) {
            recordsList.style.display = "block";
            backButton.style.display = "none";
            deleteRowButton.style.display = "none";

            const headerRow = recordsList.insertRow();
            for (const key in recordsData[0]) {
                const th = document.createElement("th");
                th.textContent = key;
                headerRow.appendChild(th);
            }

            recordsData.forEach((record) => {
                const row = recordsList.insertRow();
                for (const key in record) {
                    const cell = row.insertCell();
                    cell.textContent = record[key];
                    cell.addEventListener("click", async () => {
                        const pk = record["id"];
                        const rowData = await fetchData(`${url_list_row_model_from_pk}${pk}?model=${model}`);

                        currentRowPk = pk;
                        backButton.style.display = "block";
                        recordsHeader.textContent = "Запись";
                        deleteRowButton.style.display = "block";

                        const detailsElement = document.createElement("div");
                        detailsElement.className = "record-details";

                        for (const field in rowData) {
                            const fieldElement = document.createElement("div");
                            fieldElement.className = "field";
                            fieldElement.innerHTML = `<strong>${field}:</strong> ${rowData[field]}`;
                            detailsElement.appendChild(fieldElement);
                        }

                        recordsList.innerHTML = "";
                        recordsList.appendChild(detailsElement);
                    });
                }
            });

            currentRecordsData = recordsData;
        } else {
            const noDataRow = recordsList.insertRow();
            const noDataCell = noDataRow.insertCell();
            noDataCell.textContent = "Нет данных";
        }
    };

    backButton.addEventListener("click", async () => {
        const recordsData = await fetchData(`${url_list_rows_model}?model=${currentModel}`);
        renderRecordsTable(recordsData, currentModel);
        recordsList.style.display = "block";
        backButton.style.display = "none";
        deleteRowButton.style.display = "none";
        recordsHeader.textContent = "Список записей";
    });

    deleteRowButton.addEventListener("click", async () => {
        const recordsResponse = await deleteData(`${url_list_row_model_from_pk}${currentRowPk}?model=${currentModel}`);
        console.log(recordsResponse);
        backButton.click();
    });

    const modelsData = await fetchData(url_list_models);
    renderModelsList(modelsData);
});
