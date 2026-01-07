import { registry } from '@web/core/registry';
import { googleMapView } from '@web_view_google_map/views/google_map/google_map_view';
import { GoogleMapRendererScaffold } from './google_map_renderer';
import { GoogleMapScaffoldArchParser} from './google_map_arch_parser';
import { GoogleMapControllerScaffold } from './google_map_controller';

export const googleMapScaffoldView = {
    ...googleMapView,
    ArchParser: GoogleMapScaffoldArchParser,
    Renderer: GoogleMapRendererScaffold,
    Controller: GoogleMapControllerScaffold,
};

registry.category('views').add('google_map_scaffold', googleMapScaffoldView);
