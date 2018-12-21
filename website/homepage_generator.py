import os
import tempfile

from jinja2 import Environment as Jinja2Environment, PackageLoader, select_autoescape
from webassets import Environment as AssetsEnvironment
from webassets.ext.jinja2 import AssetsExtension


class HomepageGenerator(object):
    def __init__(self, path: str):
        self.path = path
        self.loader = PackageLoader('website', 'templates')
        self.assets_environment = AssetsEnvironment(
            directory='static',
            url='/static')
        self.jinja_environment = Jinja2Environment(
            loader=self.loader,
            autoescape=select_autoescape(['html', 'xml']),
            extensions=[AssetsExtension]
        )
        self.jinja_environment.assets_environment = self.assets_environment

        self.name = 'index.html'
        self.template = self.jinja_environment.get_template(self.name)

    def save(self):
        output = self.template.render(the='variables', go='here')
        with open(os.path.join(self.path, self.name), 'w') as f:
            f.write(output)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate HTML')
    parser.add_argument('-p', dest='path')
    args = parser.parse_args()
    if args.path is None:
        with tempfile.TemporaryDirectory() as t:
            args.path = t
    hp_gen = HomepageGenerator(args.path)
    hp_gen.save()
