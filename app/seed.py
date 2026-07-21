import os
from . import db
from .models import AdminUser, SiteSetting, ContentItem


def seed_database():
    if not AdminUser.query.first():
        user = AdminUser(name='Administrador', email=os.getenv('ADMIN_EMAIL', 'admin@site.com'))
        user.set_password(os.getenv('ADMIN_PASSWORD', 'TroqueAgora123!'))
        db.session.add(user)

    defaults = [
        ('site_name','ANICE 11888','Nome do site','Identidade',0),
        ('logo','','Logomarca','Identidade',1),
        ('favicon','','Favicon','Identidade',2),
        ('primary_color','#0432b8','Cor azul principal','Identidade',3),
        ('secondary_color','#ffd400','Cor amarela','Identidade',4),
        ('hero_eyebrow','DEPUTADA ESTADUAL','Chamada pequena','Hero',0),
        ('hero_title','ANICE','Título principal','Hero',1),
        ('hero_number','11888','Número','Hero',2),
        ('hero_tagline','CORAGEM PARA FAZER, EXPERIÊNCIA PARA TRANSFORMAR.','Frase principal','Hero',3),
        ('hero_description','Anice reúne trabalho, compromisso com o Paraná e com as pessoas. Uma voz firme na defesa da família, da educação, da saúde e da liberdade.','Descrição','Hero',4),
        ('hero_person','','Foto da pessoa','Hero',5),
        ('hero_bg','','Imagem de fundo','Hero',6),
        ('hero_btn1_text','CONHEÇA ANICE','Botão 1 - texto','Hero',7),
        ('hero_btn1_url','#sobre','Botão 1 - link','Hero',8),
        ('hero_btn2_text','ASSISTA AO VÍDEO','Botão 2 - texto','Hero',9),
        ('hero_btn2_url','#','Botão 2 - link','Hero',10),
        ('about_title','UMA TRAJETÓRIA DE LUTA E COMPROMISSO','Título','Sobre',0),
        ('about_text','Anice é empresária, mãe, mulher de fé e deputada estadual pelo Paraná. Sua história é marcada pela coragem, pela fé em Deus e pelo compromisso em trabalhar por um Paraná mais justo, próspero e com oportunidades para todos.','Texto','Sobre',1),
        ('about_image','','Imagem principal','Sobre',2),
        ('about_quote','Minha missão é servir às pessoas, defender nossos valores e construir um Paraná cada vez melhor para todos.','Citação','Sobre',3),
        ('about_signature','Anice','Assinatura','Sobre',4),
        ('cta_title','VAMOS, JUNTOS, TRANSFORMAR O PARANÁ COM CORAGEM E EXPERIÊNCIA.','Título do CTA','CTA',0),
        ('cta_text','Fale com a Anice, envie sua sugestão ou participe dessa missão!','Texto do CTA','CTA',1),
        ('cta_image','','Imagem do CTA','CTA',2),
        ('footer_text','Coragem para fazer. Experiência para transformar.','Texto do rodapé','Rodapé',0),
        ('phone','(41) 99999-11888','Telefone','Contato',0),
        ('email','contato@anice11888.com.br','E-mail','Contato',1),
        ('city','Curitiba - PR','Cidade','Contato',2),
        ('instagram','#','Instagram','Redes sociais',0),
        ('facebook','#','Facebook','Redes sociais',1),
        ('youtube','#','YouTube','Redes sociais',2),
        ('whatsapp','#','WhatsApp','Redes sociais',3),
    ]
    existing = {s.key for s in SiteSetting.query.all()}
    for key, value, label, group, order in defaults:
        if key not in existing:
            kind = 'image' if key in {'logo','favicon','hero_person','hero_bg','about_image','cta_image'} else ('color' if 'color' in key else 'text')
            db.session.add(SiteSetting(key=key, value=value, label=label, group=group, sort_order=order, kind=kind))

    section_data = {
        'stats': [
            ('+20 MIL','PESSOAS ATENDIDAS','bi-people-fill'),('+150','PROJETOS APOIADOS','bi-patch-check-fill'),('399','MUNICÍPIOS VISITADOS','bi-geo-alt-fill'),('1 MISSÃO','SERVIR E TRANSFORMAR','bi-heart-fill')],
        'areas': [
            ('FAMÍLIA E VALORES','Defesa da família, da vida e dos valores que constroem nossa sociedade.','bi-people-fill'),('EDUCAÇÃO','Apoio à educação de qualidade e formação de cidadãos.','bi-mortarboard-fill'),('SAÚDE','Mais acesso, prevenção e cuidado para todos.','bi-heart-pulse-fill'),('LIBERDADE E SEGURANÇA','Defesa da liberdade e políticas firmes para mais segurança.','bi-shield-lock-fill'),('DESENVOLVIMENTO ECONÔMICO','Incentivo ao emprego, empreendedorismo e crescimento.','bi-bar-chart-fill'),('DEFESA DO PARANÁ','Orgulho de ser paranaense e lutar pelo que é nosso.','bi-map-fill')],
        'projects': [('Educação que Transforma','Apoio a escolas, valorização de professores e incentivo à educação em tempo integral.',''),('Saúde para Todos','Mais investimentos em atenção básica, prevenção e estrutura para melhorar o atendimento.',''),('Paraná Mais Seguro','Apoio às forças de segurança, tecnologia e políticas que protegem nossas famílias.',''),('Emprego e Oportunidades','Incentivo ao empreendedorismo, qualificação profissional e geração de empregos.','')],
        'news': [('Anice participa de entrega de equipamentos para escolas','Investimento na educação é investimento no futuro do Paraná.',''),('Projeto de lei de Anice fortalece apoio às mães atípicas','Iniciativa garante mais suporte e dignidade para famílias que precisam.',''),('Anice visita municípios e ouve demandas da população','Escuta ativa e compromisso com cada canto do nosso estado.',''),('Anice defende valores e liberdade no Parlamento','Atuação firme em defesa da família, da fé e da liberdade.','')],
        'gallery': [('Momento com famílias','Registro de uma agenda especial.',''),('Encontro com lideranças','Diálogo com representantes da comunidade.',''),('Trabalho no Parlamento','Defesa de projetos importantes para o Paraná.',''),('Visita aos municípios','Presença em todas as regiões do estado.','')],
        'agenda': [('Encontro com lideranças','Sábado · 09h00','bi-calendar-event'),('Visita à Feira da Família','Domingo · 10h00','bi-calendar-event'),('Reunião com comunidade','Sábado · 14h00','bi-calendar-event'),('Caminhada por valores','Domingo · 09h00','bi-calendar-event')],
        'testimonials': [('Maria Aparecida','Anice é uma mulher de fé, humilde e determinada. Tem feito a diferença na vida de muitas famílias paranaenses.',''),('João Carlos','Sua atuação é firme, coerente e sempre voltada para o que realmente importa: as pessoas!',''),('Luciane Ribeiro','Confio no trabalho da Anice porque ela está presente, ouve e luta por um Paraná melhor para todos.','')]
    }
    for section, items in section_data.items():
        if ContentItem.query.filter_by(section=section).count() == 0:
            for i, (title, desc, icon) in enumerate(items):
                db.session.add(ContentItem(section=section,title=title,description=desc,icon=icon or 'bi-arrow-right',sort_order=i,date_text='10 MAI 2026' if section=='news' else '',location='Curitiba - PR' if section=='agenda' else ''))
    db.session.commit()
