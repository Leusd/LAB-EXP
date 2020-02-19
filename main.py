import requests
import json

headers = {"Authorization": "Bearer YOUR API KEY"}


def run_query(query):  #Metodo de chamada da API do GitHub
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


# Query do GraphQL que procura os primeiros 100 repositorios com mais de 100 estrelas.
query = """
{
  search (query:"stars:>100",type: REPOSITORY, first:100) {
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
result = run_query(query)  #Executar a Query
nodes= result["data"]["search"]["nodes"] # separar a string para exibir apenas os nodes
print(json.dumps(nodes, indent=4)) #exibir no console a string identada