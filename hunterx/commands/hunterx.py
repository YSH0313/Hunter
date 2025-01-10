# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2024/12/30 16:32
# @Version: 1.0.0
# @Description: '用于创建项目结构及模版'
import sys

import click
from InquirerPy import prompt

from hunterx.commands.tools import re_name
from hunterx.commands.complete_template import CompleteTemplate
from hunterx.commands.config import green_text, yellow_text, reset_all, custom_style


class hunterx(CompleteTemplate):

    @staticmethod
    def ui():
        # 使用PyInquirer实现光标选择
        questions = [
            {
                'type': 'confirm',
                'name': 'create_project',
                'message': f'You are about to create a new project. Please follow the prompts to fill in the information.',
                'default': True  # 默认值为 True
            },
            {
                'type': 'input',  # 项目名称
                'name': 'project_name',
                'message': f'📁Enter the project name for your project:',
                'when': lambda answers: answers.get('create_project'),  # 只有当用户选择创建项目时才显示
                'validate': lambda answer: len(answer) > 0 or 'Project name cannot be empty.'
            },
            {
                'type': 'input',  # 任务名称
                'name': 'spider_name',
                'message': f'💡Enter the task name for the project:',
                'when': lambda answers: answers.get('create_project'),  # 只有当用户选择创建项目时才显示
                'validate': lambda answer: len(answer) > 0 or 'Task name cannot be empty.'
            },
            {
                'type': 'list',
                'name': 'kernel',
                'message': '⚙️Please select a kernel:',
                'choices': ['ManagerRabbitmq', 'ManagerRedis', 'ManagerMemory'],
                'default': 'ManagerMemory',  # 默认选项
                'when': lambda answers: answers.get('create_project'),  # 只有当用户选择创建项目时才显示
                'validate': lambda answer: len(answer) > 0 or 'Kernel cannot be empty.'
            }
        ]

        # 获取用户的选择
        answers = prompt(questions, style=custom_style)

        # 输出用户选择的项目名称和任务名称
        if answers.get('create_project'):
            project_name = answers.get('project_name')
            spider_name = answers.get('spider_name')
            kernel = answers.get('kernel')

            hunterx.info(project_name, spider_name, kernel)
        else:
            print(f'{yellow_text}Project creation was aborted.')

    @staticmethod
    @click.command()
    @click.option('-p', '--project_name', prompt=True, help='The project name.')
    @click.option('-s', '--spider_name', prompt=True, help='The task name.')
    @click.option('-k', '--kernel', prompt=True, help='The kernel name.')
    def cli(project_name, spider_name, kernel):
        hunterx.info(project_name, spider_name, kernel)

    @staticmethod
    def info(project_name, spider_name, kernel):
        print(f'The project name is: {green_text}{project_name}.{reset_all}')
        print(f'The task name is: {green_text}{spider_name}.{reset_all}')
        print(f'The selected kernel is: {green_text}{kernel}.{reset_all}')

        spider_name = spider_name if spider_name else 'first_spider'

        spider_template = hunterx.get_spider_tmpl(kernel)
        pipelines_template = hunterx.get_pipelines_tmpl()
        middlewares_template = hunterx.get_middleware_tmpl()
        items_template = hunterx.get_item_tmpl()

        template_values = {
            'Class_name': re_name(spider_name),
            'spider_name': spider_name,
        }

        spider_model = spider_template.safe_substitute(template_values)
        pipelines_model = pipelines_template.safe_substitute(template_values)
        middlewares_model = middlewares_template.safe_substitute(template_values)
        items_model = items_template.safe_substitute(template_values)

        hunterx.create_project_structure(
            project_name, spider_name, spider_model, pipelines_model, middlewares_model, items_model
        )


def main():
    if len(sys.argv) > 1:
        hunterx.cli()
    else:
        hunterx.ui()


# 示例：在当前目录下创建项目
if __name__ == "__main__":
    main()
