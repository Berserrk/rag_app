Task: Label entities in a JSON dictionary with crimes from a given list.

Input:
1. JSON file with entities and descriptions
2. List of crimes: {list_of_crimes}

Rules:
- Label only the perpetrator of the crime
- If entity is not the perpetrator, label as "no label found"
- Multiple labels possible per entity

Example:
Input: {"companyA": "companyA is investing crime and money laundering that Mr. Yu commited in Japan and in Asia"}
Output: {"companyA": "no label found"}

Process each entity and provide labels in JSON format.