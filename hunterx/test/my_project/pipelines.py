from hunterx.piplines.basepipeline import Pipeline
from hunterx.test.my_project.items import MyItem


class MyProject1Pipeline(Pipeline):

    async def process_item(self, item, spider):
        if isinstance(item, MyItem):
            print(item)
            print(spider.name)
