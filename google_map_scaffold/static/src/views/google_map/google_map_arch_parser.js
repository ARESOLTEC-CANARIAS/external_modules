import { GoogleMapArchParser } from '@web_view_google_map/views/google_map/google_map_arch_parser';

export class GoogleMapScaffoldArchParser extends GoogleMapArchParser {
    parse(xmlDoc, models, modelName) {
        const archInfo = super.parse(xmlDoc, models, modelName);
        const description = xmlDoc.getAttribute('description');
        archInfo.sidebarDescriptionField = description;
        return archInfo;
    }
}
