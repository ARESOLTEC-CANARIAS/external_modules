import { GoogleMapController } from '@web_view_google_map/views/google_map/google_map_controller';

export class GoogleMapControllerScaffold extends GoogleMapController {
    getViewMapConfig() {   
        return Object.assign(super.getViewMapConfig(), {
            description: 'description',
        });
    }
}
