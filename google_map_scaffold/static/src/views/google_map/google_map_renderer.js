import { GoogleMapRenderer } from '@web_view_google_map/views/google_map/google_map_renderer';
const { markup} = owl;


export class GoogleMapRendererScaffold extends GoogleMapRenderer {
    static components = {
        ...GoogleMapRenderer.components,
    };
    /**
     * @override
     */
    get infoWindowTemplate() {
        return 'google_map_scaffold.MarkerInfoWindow';
    }


    /**
     * @override
     */
    _prepareInfoWindowValues(record, isMulti = false) {
        let values = super._prepareInfoWindowValues(record, isMulti);
        const { other } = record.dataView;
        const { description } = other;
        values.description = description ? markup(description) : '';
        return values;
    }
}
