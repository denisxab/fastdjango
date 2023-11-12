// Перейти на указанный url
function moveUrl(new_url) {
    window.location.href = new_url;
}
// Сделать HTTP GET
const fetchData = async (url) => (await fetch(url)).json();
// Сделать HTTP DELETE
const deleteData = async (url) =>
    (await fetch(url, { method: "DELETE" })).json();
// Сделать HTTP PUT
const putData = async (url, data) =>
    (
        await fetch(url, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
    ).json();
