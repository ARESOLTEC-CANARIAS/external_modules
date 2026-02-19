# docker compose run --rm odoo odoo shell -d devel < odoo/custom/src/private/scripts/fix_tasks_product.py
# Para test:
# docker compose -f test.yaml run -T --rm odoo odoo shell -d prod < odoo/custom/src/private/scripts/fix_tasks_product.py
# Para producción:
# docker compose -f prod.yaml run -T --rm odoo odoo shell -d prod < odoo/custom/src/private/scripts/fix_tasks_product.py
domain = [('timesheet_product_id', '=', False)]
batch_size = 100  # Ajusta según la capacidad de memoria
Model = env['project.task']
offset = 0

# Asignar timesheet_product_id correcto a las tareas tras separación del producto en el proyecto
while True:
    records = Model.sudo().search(domain, limit=batch_size, offset=offset)

    if not records:
        break  # Si no hay más registros, terminamos el proceso

    for record in records:
        record.timesheet_product_id = record.default_timesheet_product_id()
    env.cr.commit()  # Guarda cambios y libera memoria

    offset += batch_size  # Avanza al siguiente bloque

domain = [('activity_user_id', '=', False)]
Model = env['project.task']
offset = 0

# Asignar activity_user_id a las tareas para mostrar el logo en el informe de partes de trabajo
while True:
    records = Model.sudo().search(domain, limit=batch_size, offset=offset)

    if not records:
        break

    records._compute_activity_user_id()
    env.cr.commit()

    offset += batch_size

print("HECHO :)")
