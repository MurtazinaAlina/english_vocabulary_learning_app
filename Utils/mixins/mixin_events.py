"""
Общие события для окон приложения.
"""


class CommonEvents:

    def __init__(self):
        pass

    def on_key_release_filter_by_search(self, event, cmbbx_form, value_list):
        """ Фильтр списка в Combobox на основе пользовательского ввода """

        search_term = cmbbx_form.get().lower()              # Получаем текст, который введен в Combobox

        # Фильтруем список значений на основе введенного текста
        filtered_data = [item for item in value_list if search_term in item.lower()]
        cmbbx_form['values'] = filtered_data                # Обновляем список значений в Combobox
        if not filtered_data:                               # Если нет совпадений, очищаем поле ввода
            cmbbx_form.set("")

    def on_mouse_wheel(self, event, canvas):
        """ Прокручивание содержимого окна canvas колёсиком мыши """

        try:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except (Exception, ):
            pass
