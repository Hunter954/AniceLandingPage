import os
from . import db
from .models import AdminUser, SiteSetting, ContentItem


# Valores de campanha baseados no Kit de Comunicação fornecido.
KODAMA_DEFAULTS = [
    ('site_name','KODAMA','Nome do site','Identidade',0),
    ('logo','','Logomarca','Identidade',1),
    ('favicon','','Favicon','Identidade',2),
    ('primary_color','#0432b8','Cor principal','Identidade',3),
    ('secondary_color','#ffd400','Cor de destaque','Identidade',4),
    ('hero_eyebrow','DEPUTADO FEDERAL','Chamada pequena','Hero',0),
    ('hero_title','KODAMA','Título principal','Hero',1),
    ('hero_number','','Número de campanha','Hero',2),
    ('hero_tagline','UM COMPROMISSO REAL COM FOZ DO IGUAÇU E A FRONTEIRA','Frase principal','Hero',3),
    ('hero_description','Uma candidatura para trazer soluções técnicas e políticas às dores reais da nossa região, destravar a burocracia em Brasília, atrair investimentos e garantir que a fronteira receba o respeito que merece.','Descrição','Hero',4),
    ('hero_person','','Foto da pessoa','Hero',5),
    ('hero_bg','','Imagem de fundo','Hero',6),
    ('hero_btn1_text','CONHEÇA AS PROPOSTAS','Botão 1 - texto','Hero',7),
    ('hero_btn1_url','#projetos','Botão 1 - link','Hero',8),
    ('hero_btn2_text','','Botão 2 - texto','Hero',9),
    ('hero_btn2_url','#','Botão 2 - link','Hero',10),
    ('about_title','SOLUÇÕES REAIS PARA QUEM VIVE A FRONTEIRA','Título','Sobre',0),
    ('about_text','A candidatura de Kodama nasce da necessidade de levar as prioridades de Foz do Iguaçu e da fronteira para Brasília. O foco é viabilizar investimentos, reduzir burocracias e transformar projetos estratégicos em resultados concretos para a população.','Texto','Sobre',1),
    ('about_image','','Imagem principal','Sobre',2),
    ('about_quote','Meu papel será destravar a burocracia em Brasília, atrair investimentos e garantir que a nossa fronteira receba o respeito que merece.','Citação','Sobre',3),
    ('about_signature','Kodama','Assinatura','Sobre',4),
    ('cta_title','FOZ E A FRONTEIRA PRECISAM DE VOZ, ARTICULAÇÃO E RESULTADO EM BRASÍLIA.','Título do CTA','CTA',0),
    ('cta_text','Conheça as propostas, acompanhe a campanha e envie sua sugestão diretamente para Kodama.','Texto do CTA','CTA',1),
    ('cta_image','','Imagem do CTA','CTA',2),
    ('footer_text','Um compromisso real com Foz do Iguaçu e a Fronteira.','Texto do rodapé','Rodapé',0),
    ('phone','','Telefone','Contato',0),
    ('email','','E-mail','Contato',1),
    ('city','Foz do Iguaçu - PR','Cidade','Contato',2),
    ('instagram','#','Instagram','Redes sociais',0),
    ('facebook','#','Facebook','Redes sociais',1),
    ('youtube','#','YouTube','Redes sociais',2),
    ('whatsapp','#','WhatsApp','Redes sociais',3),
]

LEGACY_VALUES = {
    'site_name': {'ANICE 11888'},
    'hero_eyebrow': {'DEPUTADA ESTADUAL'},
    'hero_title': {'ANICE'},
    'hero_number': {'11888'},
    'hero_tagline': {'CORAGEM PARA FAZER, EXPERIÊNCIA PARA TRANSFORMAR.'},
    'hero_description': {'Anice reúne trabalho, compromisso com o Paraná e com as pessoas. Uma voz firme na defesa da família, da educação, da saúde e da liberdade.'},
    'hero_btn1_text': {'CONHEÇA ANICE'},
    'about_title': {'UMA TRAJETÓRIA DE LUTA E COMPROMISSO'},
    'about_text': {'Anice é empresária, mãe, mulher de fé e deputada estadual pelo Paraná. Sua história é marcada pela coragem, pela fé em Deus e pelo compromisso em trabalhar por um Paraná mais justo, próspero e com oportunidades para todos.'},
    'about_quote': {'Minha missão é servir às pessoas, defender nossos valores e construir um Paraná cada vez melhor para todos.'},
    'about_signature': {'Anice'},
    'cta_title': {'VAMOS, JUNTOS, TRANSFORMAR O PARANÁ COM CORAGEM E EXPERIÊNCIA.'},
    'cta_text': {'Fale com a Anice, envie sua sugestão ou participe dessa missão!'},
    'footer_text': {'Coragem para fazer. Experiência para transformar.'},
    'phone': {'(41) 99999-11888'},
    'email': {'contato@anice11888.com.br'},
    'city': {'Curitiba - PR'},
}

SECTION_DATA = {
    'stats': [
        ('R$ 200 MI','PARA VIABILIZAR O HU-UNILA','bi-hospital-fill'),
        ('US$ 1.000','PROPOSTA PARA A COTA TERRESTRE','bi-cash-coin'),
        ('4 ÁREAS','SAÚDE, AGRO, TURISMO E LOGÍSTICA','bi-cpu-fill'),
        ('1 FOCO','FOZ DO IGUAÇU E A FRONTEIRA','bi-geo-alt-fill'),
    ],
    'areas': [
        ('SAÚDE DE REFERÊNCIA','HU-UNILA e uma Lei Federal de Financiamento Específico para cidades de fronteira.','bi-heart-pulse-fill'),
        ('CIÊNCIA, TECNOLOGIA E INOVAÇÃO','Foz Hub Tech para conectar universidades, Itaipu Parquetec, laboratórios e mercado global.','bi-cpu-fill'),
        ('ECONOMIA E TURISMO','Equiparação da cota terrestre e modernização da fiscalização para uma fronteira mais ágil.','bi-graph-up-arrow'),
        ('INFRAESTRUTURA E MOBILIDADE','Reabertura imediata do Trevo do Charrua e articulação para a trincheira definitiva.','bi-sign-intersection-fill'),
    ],
    'projects': [
        ('HU-UNILA: HOSPITAL UNIVERSITÁRIO','Viabilizar a construção do Hospital Universitário da UNILA com orçamento de R$ 200 milhões, aproveitando o pré-estudo técnico existente para acelerar sua inclusão no plano de expansão da Ebserh.','bi-hospital-fill'),
        ('LEI DA SAÚDE DE FRONTEIRA','Aprovar uma Lei Federal de Financiamento Específico para cidades de fronteira, construindo uma coalizão com bancadas de outros estados para garantir repasse adicional permanente.','bi-file-earmark-medical-fill'),
        ('FOZ HUB TECH','Destinar emendas para laboratórios de MedTech, AgroTech, TurisTech e Logística Inteligente, articulando MCTI e ApexBrasil para levar tecnologias criadas em Foz ao mercado global.','bi-cpu-fill'),
        ('COTA TERRESTRE DE US$ 1.000','Articular diretamente com o Ministério da Fazenda e a Receita Federal para equiparar a cota terrestre a US$ 1.000.','bi-cash-stack'),
        ('FRONTEIRA INTELIGENTE','Modernizar a fiscalização com tecnologia de ponta e destinar emendas para PF e Receita Federal investirem em reconhecimento facial e totens digitais.','bi-shield-check'),
        ('TREVO DO CHARRUA','Defender a reabertura imediata e a construção da trincheira definitiva, com solução de curto prazo e convênio entre Itaipu, Estado e União.','bi-sign-intersection-fill'),
    ],
    'gallery': [
        ('Foz do Iguaçu','Compromisso com quem vive e trabalha na cidade.',''),
        ('Nossa fronteira','Uma região estratégica que precisa de respeito e investimento.',''),
        ('Tecnologia e inovação','Conexão entre universidades, Itaipu Parquetec e novas oportunidades.',''),
        ('Diálogo com a população','Escuta e construção de soluções para as demandas reais da região.',''),
    ],
}


def seed_database():
    if not AdminUser.query.first():
        user = AdminUser(name='Administrador', email=os.getenv('ADMIN_EMAIL', 'admin@site.com'))
        user.set_password(os.getenv('ADMIN_PASSWORD', 'TroqueAgora123!'))
        db.session.add(user)

    current = {s.key: s for s in SiteSetting.query.all()}
    for key, value, label, group, order in KODAMA_DEFAULTS:
        item = current.get(key)
        kind = 'image' if key in {'logo','favicon','hero_person','hero_bg','about_image','cta_image'} else ('color' if 'color' in key else 'text')
        if not item:
            db.session.add(SiteSetting(key=key, value=value, label=label, group=group, sort_order=order, kind=kind))
        else:
            # Rebranding seguro: troca apenas valores conhecidos do template antigo,
            # preservando personalizações já feitas pelo administrador.
            if key in LEGACY_VALUES and item.value in LEGACY_VALUES[key]:
                item.value = value
            item.label = label
            item.group = group
            item.sort_order = order
            item.kind = kind

    # Funcionalidades removidas da home e do admin.
    ContentItem.query.filter(ContentItem.section.in_(['news','agenda','testimonials'])).delete(synchronize_session=False)

    # Atualiza o conteúdo inicial do template antigo para a campanha do Kodama.
    legacy_sections = {
        'stats': ['+20 MIL','+150','399','1 MISSÃO'],
        'areas': ['FAMÍLIA E VALORES','EDUCAÇÃO','SAÚDE','LIBERDADE E SEGURANÇA','DESENVOLVIMENTO ECONÔMICO','DEFESA DO PARANÁ'],
        'projects': ['Educação que Transforma','Saúde para Todos','Paraná Mais Seguro','Emprego e Oportunidades'],
        'gallery': ['Momento com famílias','Encontro com lideranças','Trabalho no Parlamento','Visita aos municípios'],
    }
    for section, old_titles in legacy_sections.items():
        existing_items = ContentItem.query.filter_by(section=section).all()
        if not existing_items or any(i.title in old_titles for i in existing_items):
            ContentItem.query.filter_by(section=section).delete(synchronize_session=False)
            for i, (title, desc, icon) in enumerate(SECTION_DATA[section]):
                db.session.add(ContentItem(section=section, title=title, description=desc, icon=icon or 'bi-arrow-right', sort_order=i, active=True))

    db.session.commit()
