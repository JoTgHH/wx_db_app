import wx
from db_script import SQLiteDatabase, RedisDatabase


class CustomFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='Yo!')
        # Здесь вместо SQLiteDatabase можно указать RedisDatabase при условии, что у вас работает локальный
        # Redis-сервер
        self.db = SQLiteDatabase()
        self.dict = self.db.load_data()
        self.state = 1
        self.current_table = None

        #self.SetMinSize((700, 700))
        #self.SetMaxSize((700, 700))
        self.SetSize((700, 700))

        panel1 = wx.Panel(self)
        btnPanel = wx.Panel(panel1)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        self.list_wgt = wx.ListBox(panel1)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnListBoxDClick, self.list_wgt)
        self.list_wgt.SetFont(wx.Font(25, wx.DEFAULT, wx.DEFAULT, wx.DEFAULT))
        hbox1.Add(self.list_wgt, wx.ID_ANY, wx.EXPAND | wx.ALL)

        self.TablesButton = wx.Button(btnPanel, label='These are Tables', size=(90, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButtonClick, self.TablesButton)

        self.NewButton = wx.Button(btnPanel, label='New', size=(90, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButtonClick, self.NewButton)

        self.DeleteButton = wx.Button(btnPanel, label='Delete', size=(90, 30))
        self.Bind(wx.EVT_BUTTON, self.OnButtonClick, self.DeleteButton)

        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox1.Add(self.TablesButton, wx.ID_ANY)
        vbox1.Add(self.NewButton, wx.ID_ANY)
        vbox1.Add(self.DeleteButton, wx.ID_ANY)

        btnPanel.SetSizer(vbox1)
        hbox1.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 20)

        panel1.SetSizer(hbox1)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self._update_tables()
        self.Show()

    def OnButtonClick(self, e: wx.Event):
        source = e.GetEventObject()
        if source == self.TablesButton:
            self.state = 1
            self.TablesButton.SetLabel('These are Tables')
            self.current_table = None
            self._update_tables()
        elif source == self.NewButton:
            if self.state == 1:
                new_table_name = wx.GetTextFromUser('Enter a new table name', 'Create a new table')
                if new_table_name == '':
                    return
                self.dict[new_table_name] = list()
                self._update_tables()
            elif self.state == 2:
                selected_table = self.current_table
                new_article_text = wx.GetTextFromUser('Enter a new article text', 'Create an article')
                if new_article_text == '':
                    return
                articles_list = self.dict[selected_table]
                articles_list.append(new_article_text)
                self.dict[selected_table] = articles_list
                self._update_articles(selected_table)
        elif source == self.DeleteButton:
            if self.state == 1:
                table_name = self.list_wgt.GetStringSelection()
                del self.dict[table_name]
                self._update_tables()
            elif self.state == 2:
                selected_table = self.current_table
                selected_text = self.list_wgt.GetStringSelection()
                articles_list = self.dict[selected_table]
                for x in range(len(articles_list)):
                    if articles_list[x] == selected_text:
                        articles_list.pop(x)
                        break
                self._update_articles(selected_table)

    def OnListBoxDClick(self, e):
        if self.state == 1:
            selected_table = self.list_wgt.GetStringSelection()
            self._update_articles(selected_table)
            self.state = 2
            self.TablesButton.SetLabel('These are Articles')
            self.current_table = selected_table
        elif self.state == 2:
            selected_text = self.list_wgt.GetStringSelection()
            selected_table = self.current_table
            edit_text = wx.GetTextFromUser('Edit text')
            if edit_text == '':
                return
            articles_list = self.dict[selected_table]
            for x in range(len(articles_list)):
                if articles_list[x] == selected_text:
                    articles_list[x] = edit_text
            self.dict[selected_table] = articles_list
            self._update_articles(selected_table)

    def _update_articles(self, selected_table):
        self.list_wgt.Clear()
        articles = self.dict[selected_table]
        for x in articles:
            self.list_wgt.Append(x)

    def _update_tables(self):
        self.list_wgt.Clear()
        entries = self.dict.keys()
        for x in entries:
            self.list_wgt.Append(x)

    def OnClose(self, e):
        self.db.save_data(self.dict)
        self.Destroy()
