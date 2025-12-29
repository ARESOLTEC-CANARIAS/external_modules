import {patch} from "@web/core/utils/patch";
import {GoogleMapRenderer} from "@web_view_google_map/views/google_map/google_map_renderer";

patch(GoogleMapRenderer.prototype, {
    /**
     * Create marker options
     * @private
     * @param {Object} geolocation Latitude/longitude object
     * @param {Object} data Record data
     * @returns {Object} Marker options
     */
    _createMarkerOptions(geolocation, data) {
        const options = super._createMarkerOptions(...arguments);
        options.gmpDraggable = true;
        return options;
    },

    /**
     * Create a new marker
     * @private
     * @param {Object} record Record data
     * @param {Object} geolocation Position data
     * @param {Object} data Additional marker data
     * @param {Object} pinElement Pin element
     * @param {Object} elementValues Values for marker styling
     * @param {Class} AdvancedMarkerElement Google Maps marker class
     * @returns {Object} New marker
     */
    _createNewMarker(record, geolocation, data, pinElement, elementValues, AdvancedMarkerElement) {
        const marker = super._createNewMarker(...arguments);

        const dragendListener = marker.addListener(
            'dragend',
            this._handleMarkerDragend.bind(this, marker)
        );
        this._storeMarkerEventListener(record.id, 'dragend', dragendListener);

        // Store marker in cache
        this.cache.set(record.id, marker);

        // Update map bounds
        this._updateMapBounds(marker);

        return marker;
    },

    /**
     * Add event 'dragend' listener to marker and manage marker located at the same coordinate
     * @param {Object} marker
     */
    async _handleMarkerDragend(marker) {
        try {
            const position = marker.position;
            const {latitudeField, longitudeField} = this.props.archInfo;
            await this.props.list.model.orm.write(
                this.props.list.resModel,
                [marker._odooRecord.resId],
                {
                    [latitudeField]: position.lat,
                    [longitudeField]: position.lng,
                }
            );
            marker._odooRecord.data[latitudeField] = position.lat;
            marker._odooRecord.data[longitudeField] = position.lng;
        } catch (err) {
            console.error("Odoo save error:", err);
        }
    },

});
