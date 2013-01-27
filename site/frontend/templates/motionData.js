$def with (timeline)
{
cols: [
        ["string", "Byty podle velikosti"],
        ["number", "Rok"],
        ["number", "Cena"],
        ["number", "Cena za m²"],
        ["number", "Cena za m²"],
        ["number", "Plocha"]
        ],
rows: [
$for separator, tpointGroups in separate(",", timeline):
    ${separator}
    $for separator, group in separate(",", tpointGroups[1]):
        ${separator}[$jsnize(group[0]),$tpointGroups[0],$group[2],$group[3],$group[3],$group[4]]
]}
