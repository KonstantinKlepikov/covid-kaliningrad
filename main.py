import os
import streamlit as st
import numpy as np
import pandas as pd
import supportFunction as sfunc
from drawTools import Linear, Point, Area, Bar


__version__ = '1.3'


def main(hidemenu=True):

    # hide streamlit menu
    if hidemenu:
        hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>

        """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

    st.sidebar.title('Данные о covid-19 в Калининградской области')
    st.sidebar.text('v' + __version__)

    # prepare data for drawing
    p, paginator = sfunc.pagemaker() # paginator
    data = sfunc.dataloader('https://raw.githubusercontent.com/KonstantinKlepikov/covid-kaliningrad/datasets/data/data.csv')
    rosstat = sfunc.dataloader('https://raw.githubusercontent.com/KonstantinKlepikov/covid-kaliningrad/datasets/data/rosstat.csv')
    invitro = sfunc.invitroCases(data[['дата', 'total', 'positive']])
    ds = sfunc.asidedata(data, rosstat) # data for aside menu
    high, low = sfunc.irDestrib(data)
    _colsPro = sfunc.profession(data)
    _colsReg = sfunc.regDistr(data)

    # aside menu
    st.sidebar.markdown('Обновлено: {}'.format(ds['update']))
    st.sidebar.markdown('Всего выявлено: **{0}** ({1}%)'.format(ds['sick'], ds['proc']))
    st.sidebar.markdown('Официально умерло: **{}**'.format(ds['dead']))
    st.sidebar.markdown('Общая летальность: **{}%**'.format(ds['let']))
    st.sidebar.markdown('Выписано: **{}**'.format(ds['ex']))
    st.sidebar.markdown('Привито (Ф1): **{0}** ({1}%)'.format(ds['pr1'], ds['prproc1']))
    st.sidebar.markdown('Привито (Ф2): **{0}** ({1}%)'.format(ds['pr2'], ds['prproc2']))
    st.sidebar.markdown('IR4 >= 1 дней: **{}**'.format(high))
    st.sidebar.markdown('IR4 < 1 дней: **{}**'.format(low))
    st.sidebar.markdown('Смерти связанные с covid(росстат):')
    st.sidebar.markdown('на {}'.format(ds['rstat_date']))
    st.sidebar.markdown('умерло: {}'.format(ds['rstat_dead']))    
    st.sidebar.markdown('летальность: {}%'.format(ds['rstat_let']))


    # main content
    page = st.radio('Данные', paginator)


    if page == 'intro':
        st.header(p[page])

        st.subheader('Описание проекта')
        st.markdown('Проект работает с открытыми данными, собранными из различных официальных источников. \
            Данные обновляются в конце дня. Предсталеные визуализированные данные не являются точными и не могут \
            отражать истинную картину распространения covid-19 в Калининградской области. Автор проекта агрегирует \
            данные с образовательной целью и не несет ответственности за их достоверность. Весь контент и код \
            проекта предоставляется по [MIT лицензии](https://opensource.org/licenses/mit-license.php).')

        st.subheader('Как это сделано?')
        st.markdown('[Статья о том, как собрано это приложение](https://konstantinklepikov.github.io/2021/01/10/zapuskaem-machine-learning-mvp.html)')
        st.markdown('[Репозиторий проекта](https://github.com/KonstantinKlepikov/covid-kaliningrad)')
        st.markdown('[Данные](https://docs.google.com/spreadsheets/d/1iAgNVDOUa-g22_VcuEAedR2tcfTlUcbFnXV5fMiqCR8/edit#gid=1038226408)')

        st.subheader('Изменения в версиях')
        st.markdown('**v1.3** Удалены выбросы из данных.')
        st.markdown('**v1.2** Улушено отображение на мобильных устройствах. Оптимизирована скорость загрузки \
            страницы. Добавлены IR7 и распределение IR, распределения, данные Росстата, invitro, вакцинация.')
        st.markdown('**v1.1** Добавлена обработка данных и вывод основных визуализаций.')

        st.subheader('Контакты')
        st.markdown('[Мой блог про machine learning](https://konstantinklepikov.github.io/)')
        st.markdown('[Я на github](https://github.com/KonstantinKlepikov)')
        st.markdown('[Мой сайт немножко про маркетинг](https://yorb.ru/)')
        st.markdown('[Телеграм](https://t.me/KlepikovKonstantin)')
        st.markdown('[Фейсбук](https://facebook.com/konstatin.klepikov)')

        st.markdown('К сожалению официальные службы не поделились со мной имеющимися историческими данными. Буду благодарен \
            за любой источник данных, если таковой имеется - пишите в [телеграм](https://t.me/KlepikovKonstantin).')
        st.image('https://raw.githubusercontent.com/KonstantinKlepikov/covid-kaliningrad/main/img/answer.png', use_column_width=True)

    
    elif page == 'cases':
        st.header(p[page])

        # cases
        ch = Linear(
            p[page], 
            data[['дата', 'всего', 'ОРВИ', 'пневмония', 'без симптомов']]
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.selectionchart())

        # area cases
        ch = Area(
            p[page], 
            data[['дата', 'ОРВИ', 'пневмония', 'без симптомов']],
            height=400
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())
        
        # cumsum cases
        ch = Linear(
            'Количество случаев аккумулировано', 
            data[['дата', 'кумул. случаи']], 
            height=400, 
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())
        
        # 30/1000
        ch = Linear(
            'Количество случаев на 1000 человек за последние 30 дней', 
            data[['дата', '30days_1000']], 
            height=400, 
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())

        # invitro cases
        st.subheader('Данные о случаях, выявленных в сети клиник Invitro (IgG)')
        st.markdown('Нет сведений о том, что данные случаи учитываются в статистике Роспотребнадзора. Сведения \
            получены на сайте [invitro.ru](https://invitro.ru/l/invitro_monitor/)')

        ch = Linear(
            'Кейсы в Invitro', 
            data[['дата', 'positive']],
            height=400
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.selectionchart())

        # invitro cases cumulative
        ch = Linear(
            'Кейсы в Invitro аккумулировано', 
            data[['дата', 'positivecum']],
            height=400
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())


    elif page == 'infection rate':
        st.header(p[page])

        # ir4
        st.markdown('IR4 расчитывается по методике Роспотребнадзора - как отношение количества заболевших за прошедшие \
            4 дня к количеству заболевших за предыдущие прошедшие 4 дня.')
        ch = Linear(
            'Infection Rate 4 days', 
            data[['дата', 'infection rate']], 
            level=1
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.baselinechart())

        # ir7
        ch = Linear(
            'Infection Rate 7 days', 
            data[['дата', 'IR7']], 
            level=1
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.baselinechart())

        # ir difference
        ch = Linear(
            'Распределение отношения количества дней с положительным ir4 к количеству дней с отрицательным ir4', 
            data[['дата', 'отношение']], 
            level=1
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.baselinechart())


    elif page == 'deaths':
        st.header(p[page])

        # deaths with polynomial
        ch = Area(
            'умерли от ковид', 
            data[['дата', 'умерли от ковид']],
            height=400, 
            interpolate='step', 
            poly=7,
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.polynomialchart())

        # death cumsum
        ch = Linear(
            'смертельные случаи нарастающим итогом', 
            data[['дата', 'кумул.умерли']], 
            height=400, 
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())

        # hospital death data
        st.markdown('Информация об умерших в палатах, отведенных для больных для больных пневмонией/covid предоставлялась \
            мед.службами по запросу [newkaliningrad.ru](https://www.newkaliningrad.ru/)')
        ch = Linear(
            'умерли в палатах для ковид/пневмонии', 
            data[['дата', 'умерли в палатах для ковид/пневмония с 1 апреля']].query("'2020-11-01' <= дата & `умерли в палатах для ковид/пневмония с 1 апреля` > 0"), 
            height=400, 
            point=True, 
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())

        # rosstat death
        rosstat_ = rosstat.copy(deep=True)
        rosstat_['Месяц'] = pd.to_datetime(rosstat_['Месяц'], dayfirst=True)
        ch = Area(
            'Данные Росстата о смертности с диагнозом COVID-19', 
            rosstat_, 
            target='Месяц',
            height=400,
            width=800
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.emptychart())


    elif page == 'exits':
        st.header(p[page])

        # exit
        st.markdown('Нет достоверной информации о том, что лечение выписанных больных в действительности закончено')
        ch = Linear(
            'Выписаны', 
            data[['дата', 'всего', 'выписали']], 
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.selectionchart())

        # cumsum exit
        ch = Linear(
            'Выписаны из больниц нарастающим итогом', 
            data[['дата', 'кумул. случаи', 'кумул.выписаны']], 
            height=400, 
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())


    elif page == 'capacity':
        st.header(p[page])
        st.markdown('Активные случаи - это заразившиеся минус выписанные и умершие. Ежедневные данные о количестве \
            болеющих и госпитализированных не проситавляются. Данные о загруженности больниц предоставлены нерегулярно.')

        # cumsum minus exit
        ch = Linear(
            'Активные случаи нарастающим итогом', 
            data[['дата', 'кумул.активные']], 
            height=400, 
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())

        # hospital places
        df = sfunc.slicedData(
            data[['дата', 'доступно под ковид', 'занято под ковид', 'доступно ИВЛ', 'занято ИВЛ', 'доступно под ковид и пневмонию', 
                'занято под ковид и пневмонию']],
            "'2020-11-01' <= дата "
            )
        ch = Point(
            'Доступные места', 
            df, 
            height=800, 
            grid=False, 
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())


    elif page == 'tests':
        st.header(p[page])

        # tests
        ch = Linear(
            'Общее количество тестов', 
            data[['дата', 'кол-во тестов']], 
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.selectionchart())

        # tests cumulative
        ch = Linear(
            'Общее количество тестов аккумулировано', 
            data[['дата', 'кол-во тестов кумул']], 
            height=400, 
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())

        # tests and cases
        st.markdown('Для наглядности, количество тестов разделено на 10 для приведенных графиков.')
        ch = Linear(
            'Тестирование и распространение болезни', 
            data[['дата', 'ОРВИ', 'пневмония', 'без симптомов', 'кол-во тестов / 10']], 
            height=500
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.selectionchart())

        # tests and exit
        ch = Linear(
            'Тестирование и выписка', 
            data[['дата', 'выписали', 'кол-во тестов / 10']], 
            height=500,
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.selectionchart())

        # invitro tests
        st.subheader('Данные о тестах, проведенных в сети клиник Invitro (IgG)')
        st.markdown('Нет сведений о том, что данные о тестах invitro учитываются в статистике Роспотребнадзора. \
            Сведения получены на сайте [invitro.ru](https://invitro.ru/l/invitro_monitor/)')

        ch = Linear(
            'Кейсы в Invitro', 
            data[['дата', 'positive', 'negative']]
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.selectionchart())

        # invitro tests cumulative
        ch = Linear(
            'Тесты в Invitro аккумулирован', 
            data[['дата', 'totalcum']], 
            height=600
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())

        # invitro cases cumulative
        ch = Linear(
            'Тесты в Invitro аккумулировано (на фоне общего числа официально зафиксированных случаев)', 
            data[['дата', 'кумул. случаи', 'positivecum', 'negativecum']], 
            height=600
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())

        # invitro cases shape
        ch = Linear(
            '% положительных тестов в Invitro', 
            invitro[['дата', 'shape']],
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.selectionchart())


    elif page == 'vaccination':
        st.header(p[page])
        st.markdown('В значение поступившей вакцины и к значениям привитых официальной статистикой отнесены 300 доз \
            экспериментальной вакцины (20% плацебо). Сообщалось, что прививку получили чиновники (губернатор Калининградской области)\
            Кроме того, сообщалось, что по оканчанию эксперимента все, кто получаил плацебо, будут привиты действующим препаратом.\
            Сведений о том, что все участники эксперимента действительно получиили настоящий препарат не имеется.')

        # vaccine income
        ch = Area(
            'Поступиление вакцин', 
            data[['дата', 'поступило кумулятивно']],
            height=400
            )
        ch.legend=None
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())

        # vaccination outcome
        df = sfunc.slicedData(
            data[['дата', 'компонент 1', 'компонент 2']],
            "'2020-08-01' <= дата "
            )
        ch = Point(
            'Использовано вакцин',
            df, 
            height=400, 
            )
        ch.draw()
        ch.richchart()
        st.altair_chart(ch.emptychart())


    elif page == 'regions':
        st.header(p[page])

        # Kaliningrad and regions
        ch = Area(
            'Калининград и регионы', 
            data[['дата', 'Калининград', 'все кроме Калининграда']], 
            interpolate='step', 
            height=400,
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())

        # All regions
        ch = Area(
            'Распределение случаев по региону', 
            data[_colsReg], 
            interpolate='step', 
            height=600,
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())


    elif page == 'regions detail':

        # regions by city
        st.header('Распределение по регионам (подробнее)')
        multichart = sfunc.precision('Калининград', data[['дата', 'Калининград']])
        for i in _colsReg:
            if i != 'дата' and i != 'Калининград':
                multichart = multichart & sfunc.precision(i, data[['дата', i]])
        st.altair_chart(
            multichart
            )


    elif page == 'demographics':
        st.header(p[page])

        # activivty
        ch = Area(
            'Распределение случаев по статусу', 
            data[['дата', 'воспитанники/учащиеся', 'работающие', 'служащие', 'неработающие и самозанятые', 'пенсионеры']], 
            interpolate='step', 
            height=400,
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())

        # profession diagram
        ch = Area(
            'Распределение случаев по роду деятельности', 
            data[_colsPro], 
            interpolate='step', 
            height=600,
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())

        # sex
        ch = Area(
            'Распределение случаев по полу', 
            data[['дата', 'мужчины', 'женщины']], 
            interpolate='step', 
            height=400,
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())

        # age destribution
        _colsAge = sfunc.ageDestr(data)
        ch = Area(
            'Распределение случаев по возрасту', 
            data[_colsAge], 
            interpolate='step', 
            height=400,
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())

        # source
        ch = Area(
            'Распределение по источнику заражения', 
            data[['дата', 'завозные', 'контактные', 'не установлены']], 
            interpolate='step', 
            height=400,
            )
        ch.draw()
        ch.leanchart()
        st.altair_chart(ch.selectionchart())

    
    elif page == 'demographics detail':

        # profession destribution by profession
        st.header('Распределение по деятельности (подробнее)')
        multichart = sfunc.precision('>пенсионеры', data[['дата', '>пенсионеры']])
        for i in _colsPro:
            if i != 'дата' and i != '>пенсионеры':
                multichart = multichart & sfunc.precision(i, data[['дата', i]])
        st.altair_chart(
            multichart
            )


main()
