import { RELAUNCH } from '../../../lib/site';
import { feed, FEED_KEYS } from '../../../lib/feeds';
// No section feeds while the site is on hold for the relaunch.
export const getStaticPaths = () => RELAUNCH ? [] : FEED_KEYS.map((k) => ({ params: { feed: k } }));
export const GET = ({ params }: { params: { feed: string } }) => feed('hi', params.feed);
