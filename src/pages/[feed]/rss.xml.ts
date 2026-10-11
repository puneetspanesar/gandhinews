import { feed, FEED_KEYS } from '../../lib/feeds';
export const getStaticPaths = () => FEED_KEYS.map((k) => ({ params: { feed: k } }));
export const GET = ({ params }: { params: { feed: string } }) => feed('en', params.feed);
