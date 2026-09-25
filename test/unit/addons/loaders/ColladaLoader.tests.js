import { ColladaLoader } from '../../../../examples/jsm/loaders/ColladaLoader.js';

export default QUnit.module( 'Addons', () => {

	QUnit.module( 'Loaders', () => {

		QUnit.module( 'ColladaLoader', () => {

			QUnit.test( 'attributes of polygons with more than four vertices match positions', async ( assert ) => {

				const loader = new ColladaLoader();
				const collada = await loader.loadAsync( '/examples/models/collada/skin_and_morph.dae' );

				const mesh = collada.scene.getObjectByProperty( 'isSkinnedMesh', true );
				const attributes = mesh.geometry.attributes;
				const count = attributes.position.count;

				assert.strictEqual( attributes.normal.count, count, 'normal count matches position count' );
				assert.strictEqual( attributes.uv.count, count, 'uv count matches position count' );
				assert.strictEqual( attributes.skinIndex.count, count, 'skinIndex count matches position count' );
				assert.strictEqual( attributes.skinWeight.count, count, 'skinWeight count matches position count' );

			} );

		} );

	} );

} );
