from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style

class MenuSelector:
    def __init__(self, options):
        self.options = options
        self.selected_index = 0
        self.app = None

    def get_tokens(self):
        tokens = []
        tokens.append(('class:total', '•   请选择一个选项' + '\n'))
        tokens.append(('class:border', '+' + '-' * 20 + '+\n'))
        for i, option in enumerate(self.options):
            if i == self.selected_index:
                tokens.append(('class:border', '|'))
                tokens.append(('class:selected-star', '☆ '))
                tokens.append(('class:selected-option', option.ljust(15)))
                tokens.append(('class:border', ' |\n'))
            else:
                tokens.append(('class:border', '|  '))
                tokens.append(('class:unselected', option.ljust(15)))
                tokens.append(('class:border', ' |\n'))
        tokens.append(('class:border', '+' + '-' * 20 + '+\n'))
        return tokens

    def get_key_bindings(self):
        kb = KeyBindings()

        @kb.add('up')
        def _(event):
            self.selected_index = (self.selected_index - 1) % len(self.options)

        @kb.add('down')
        def _(event):
            self.selected_index = (self.selected_index + 1) % len(self.options)

        @kb.add('enter')
        def _(event):
            event.app.exit(result=self.options[self.selected_index])

        @kb.add('c-c')
        def _(event):
            event.app.exit(result=None)

        @kb.add('c-b')
        def _(event):
            pass

        return kb

    def run(self):
        style = Style.from_dict({
            'total': '#ffffff bold',
            'selected-star': '#ff8f8f bold',
            'selected-option': '#ffffff bold',
            'unselected': '#888888',
            'border': '#ffffff',
        })

        layout = Layout(
            HSplit([
                Window(
                    FormattedTextControl(self.get_tokens),
                    height=len(self.options) + 3,
                    wrap_lines=True,
                ),
            ])
        )

        self.app = Application(
            layout=layout,
            key_bindings=self.get_key_bindings(),
            full_screen=True,
            style=style,
            mouse_support=True,
        )

        result = self.app.run()
        if result:
            print(f'你选择了: {result}')
        else:
            print('已退出')

if __name__ == '__main__':
    options = ['选项1', '选项2', '选项3', '选项4']
    selector = MenuSelector(options)
    selector.run()