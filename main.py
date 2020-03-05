import os
import time
import requests
import csv

headers = {"Authorization": "Bearer YOUR KEY HERE"}

print("Iniciando processo")
def run_query(json, headers):  # Função que executa uma request pela api graphql
    request = requests.post('https://api.github.com/graphql', json=json,
                            headers=headers)  # efetua uma requisição post determinando o json com a query recebida
    while (request.status_code == 502):
        time.sleep(2)
        request = requests.post('https://api.github.com/graphql', json=json, headers=headers)
    if request.status_code == 200:
        return request.json()  # json que retorna da requisição
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


# Query do GraphQL que procura os primeiros 1000 repositorios com mais de 100 estrelas.
query = """
query example{
  search (query:"stars:>100",type: REPOSITORY, first:20{AFTER}) {
      pageInfo{
       hasNextPage
        endCursor
      }
      nodes {
        ... on Repository {
          nameWithOwner
          createdAt
          pullRequests(states: MERGED){
            totalCount
          }
          releases{
            totalCount
          }
          updatedAt
          primaryLanguage{
            name
          }
          closedIssues : issues(states: CLOSED){
            totalCount
          }
          totalIssues: issues{
            totalCount
          }
        }
      }
    }
}
"""

finalQuery = query.replace("{AFTER}", "")

json = {
    "query": finalQuery, "variables": {}
}

total_pages = 1
print("Executando Query\n[", end = '')
result = run_query(json, headers)  # Executar a Query
nodes = result["data"]["search"]["nodes"]  # separar a string para exibir apenas os nodes
next_page = result["data"]["search"]["pageInfo"]["hasNextPage"]

page = 0
while next_page and total_pages < 50:
    total_pages += 1
    cursor = result["data"]["search"]["pageInfo"]["endCursor"]
    next_query = query.replace("{AFTER}", ", after: \"%s\"" % cursor)
    json["query"] = next_query
    result = run_query(json, headers)
    nodes += result['data']['search']['nodes']
    next_page = result["data"]["search"]["pageInfo"]["hasNextPage"]
    print(".", end = '')
print("]")

if os.path.exists("repos.csv"):
    os.remove("repos.csv")
print("Criando arquivo CSV")
file = open("repos.csv", 'wt')
repositore = csv.writer(file)

repositore.writerow(('nameWithOwner', 'createdAt', 'pullRequests/totalCount',  # Adicionando cabecalho
                     'releases/totalCount', 'updatedAt', 'primaryLanguage/name',
                     'closedIssues/totalCount', 'totalIssues/totalCount'))
print("Salvando Repositorios:\n[", end = '')
num = 0
for node in nodes:
    if node['primaryLanguage'] is None:
        primaryLanguage = "null"
    else:
        primaryLanguage = str(node['primaryLanguage']['name'])
        # Adicionando dados de cada repositorio
        repositore.writerow((node['nameWithOwner'], node['createdAt'], str(node['pullRequests']['totalCount']),
                             str(node['releases']['totalCount']), node['updatedAt'], primaryLanguage,
                             str(node['closedIssues']['totalCount']), str(node['totalIssues']['totalCount'])))
        ++num
        if (num%10)==0:
            print(".", end = '')
print("]\nProcesso concluido")
file.close()
