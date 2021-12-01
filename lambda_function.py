
import AO3
import boto3


def input_author(author_name):

    if author_table.get_item(Key = {'author_name': author_name}):
        return

    user = AO3.User(author_name)

    works_associated=[]

    for work in user.get_works():
        if the_fandom in work.fandoms:
            works_associated.append(work.id)
    for work in user.get_bookmarks():
        if the_fandom in work.fandoms:
            works_associated.append(work.id)

    author_table.put_item(
        Item={'author_name': author_name,
            'related_works': works_associated}
    )



if __name__ == '__main__':

    dynamodb = boto3.resource('dynamodb')
    author_table = dynamodb.create_table(
        TableName='authors',
        KeySchema=[{  'AttributeName': 'author_name','KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'author_name','AttributeType': 'S'}],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
    work_table = dynamodb.create_table(
        TableName='works',
        KeySchema=[{'AttributeName': 'work_id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'work_id', 'AttributeType': 'N'}],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )

    work_table.meta.client.get_waiter('table_exists').wait(TableName='works')
    author_table.meta.client.get_waiter('table_exists').wait(TableName='authors')

    AO3.utils.limit_requests()
    the_fandom = "The Good Place (TV)"
    search = AO3.Search(fandoms=the_fandom)
    search.update()

    for i in range(1,search.pages+1):
        search.page=i
        search.update()
        for result in search.results:
            work_authors = []
            #ignores the work that's published anonymously
            if result.authors[0].username=='Anonymous':
                continue

            for author in result.authors:
                input_author(author.username)
                work_authors.append(author.username)
            work_table.put_item(
                Item={'work_id': result.id,
                    'nchapters': result.nchapters,
                    'nwords': result.words,
                    'kudos': result.kudos,
                    'hits': result.hits,
                    'authors': work_authors,
                      'rating': work.rating
                      })


