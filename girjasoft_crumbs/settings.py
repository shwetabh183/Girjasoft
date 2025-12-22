from girjasoft.settings import TEMPLATES

TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "girjasoft_crumbs.context_processors.breadcrumbs",
)
